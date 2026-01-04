import json
import os
from pathlib import Path
from datetime import datetime

import requests
from fastapi import FastAPI, HTTPException, Depends, Header, UploadFile, File, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Tuple
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import httpx

from utils.config import get_settings, ensure_required_keys
from utils.chroma_retriever import ChromaRetriever
from utils.function_schemas import FUNCTION_SCHEMAS, execute_function
from utils.auth import authenticate_student, create_jwt_token, decode_jwt_token, get_student_by_id
from utils.automation import get_student_profile
from utils.conversation_history import (
    save_conversation,
    get_conversation_history,
    save_feedback,
    get_most_asked_questions,
    get_conversation_stats,
    get_recent_feedback
)

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

app = FastAPI(title="RAG + Automation Chatbot", version="0.2.0")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Add CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # React default
        "http://localhost:5173",  # Vite default
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "https://college-chatbot-frontend.onrender.com",  # Render frontend
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

settings = get_settings()
ensure_required_keys(settings)

# Ensure upload directory exists
UPLOAD_DIR = Path("data/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Lazy-load retriever to avoid import-time failures if Chroma data is missing.
_retriever: Optional[ChromaRetriever] = None


def get_retriever() -> Optional[ChromaRetriever]:
    global _retriever
    if _retriever is None:
        try:
            _retriever = ChromaRetriever(chroma_dir=settings.chroma_dir)
        except Exception:
            _retriever = None
    return _retriever


class Message(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: List[Message]
    tools_enabled: bool = False
    user_id: Optional[str] = None
    student_context: Optional[str] = None  # optional profile/role info for prompting


class ChatResponse(BaseModel):
    reply: str
    sources: List[str] = []
    actions: List[str] = []
    model: Optional[str] = None


class LoginRequest(BaseModel):
    student_id: str
    password: str


class LoginResponse(BaseModel):
    success: bool
    token: Optional[str] = None
    profile: Optional[Dict] = None
    message: str


class FeedbackRequest(BaseModel):
    conversation_id: int
    rating: int  # 1 for thumbs up, -1 for thumbs down
    comment: Optional[str] = None


class FeedbackResponse(BaseModel):
    success: bool
    feedback_id: int
    message: str


class AppointmentRequest(BaseModel):
    faculty_id: str
    date: str  # YYYY-MM-DD
    time_slot: str  # e.g., "10:00-10:30"


class LeaveRequest(BaseModel):
    from_date: str  # YYYY-MM-DD
    to_date: str  # YYYY-MM-DD
    reason: str


class UploadResponse(BaseModel):
    success: bool
    filename: str
    filepath: str
    size: int
    message: str


def get_current_student(authorization: Optional[str] = Header(None)) -> Optional[str]:
    """Dependency to extract student_id from JWT token in Authorization header."""
    if not authorization or not authorization.startswith("Bearer "):
        return None
    token = authorization[7:]  # Remove 'Bearer ' prefix
    payload = decode_jwt_token(token)
    if not payload:
        return None
    return payload.get("student_id")


def build_system_prompt(college_name: str, student_context: Optional[str]) -> str:
    """Construct a college-specific system prompt with optional student context."""
    base_prompt = (
        f"You are a helpful college assistant for {college_name}. "
        "You help students with course information, schedules, faculty details, campus facilities, and administrative queries. "
        "Be concise, friendly, and accurate. If unsure, say so. Always cite sources when available."
    )

    if student_context:
        base_prompt += f"\nStudent context: {student_context}"

    # Guardrails
    base_prompt += (
        "\nInstructions:"
        "\n- Prefer factual, grounded answers over speculation."
        "\n- Cite sources in-line (e.g., [catalog], [faculty], [handbook]) when data is provided."
        "\n- Keep responses short unless the user asks for detail."
    )
    return base_prompt


def call_llm(messages: List[Dict[str, str]], model_name: str) -> Dict[str, str]:
    """Route to OpenAI or Anthropic; gracefully degrade if SDK or key missing."""
    # Groq path when MODEL_NAME starts with "groq-"
    if model_name.lower().startswith("groq-"):
        try:
            from groq import Groq  # type: ignore
        except Exception:
            return {"reply": "LLM unavailable (Groq SDK not installed).", "model": model_name}

        if not settings.groq_api_key:
            return {"reply": "LLM unavailable (missing GROQ_API_KEY).", "model": model_name}

        try:
            client = Groq(api_key=settings.groq_api_key)
            resp = client.chat.completions.create(
                model=model_name[5:] or model_name,  # strip "groq-" prefix
                messages=messages,
                temperature=0.2,
                max_tokens=600,
            )
            return {
                "reply": resp.choices[0].message.content or "(empty reply)",
                "model": model_name,
                "actions": [],
            }
        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"LLM Groq error: {type(e).__name__}: {e}")
            return {"reply": f"LLM call failed: {e}", "model": model_name}

    # Local LLM path (e.g., Ollama) when MODEL_NAME starts with "local-"
    if model_name.lower().startswith("local-"):
        local_model = model_name[6:] or model_name
        try:
            resp = requests.post(
                settings.local_llm_url,
                json={
                    "model": local_model,
                    "messages": messages,
                    "stream": False,
                },
                timeout=60,
            )
            resp.raise_for_status()
            data = resp.json()

            # Ollama returns {"message": {"content": "..."}}; fall back to content field if present
            content = (
                data.get("message", {}).get("content")
                or data.get("content")
                or data.get("response")
                or "(empty reply)"
            )

            return {"reply": content, "model": local_model, "actions": []}
        except Exception as e:
            return {"reply": f"LLM call failed (local): {e}", "model": model_name, "actions": []}

    # OpenAI path
    if model_name.lower().startswith("gpt"):
        try:
            import openai  # type: ignore
        except Exception:
            return {"reply": "LLM unavailable (OpenAI SDK not installed).", "model": model_name}

        if not settings.openai_api_key:
            return {"reply": "LLM unavailable (missing OPENAI_API_KEY).", "model": model_name}

        try:
            # Strip proxy env vars inside the process to avoid SDK kwargs mismatches
            for key in ["HTTPS_PROXY", "HTTP_PROXY", "ALL_PROXY", "https_proxy", "http_proxy", "all_proxy"]:
                os.environ.pop(key, None)

            proxy = None  # explicit: do not pass proxies kw to OpenAI client
            http_client = None

            try:
                client = openai.OpenAI(api_key=settings.openai_api_key, http_client=http_client)
            except TypeError as te:
                if "proxies" in str(te):
                    print("OpenAI client init hit proxies TypeError; retrying without http_client")
                    client = openai.OpenAI(api_key=settings.openai_api_key)
                else:
                    raise
            # First pass with tool calling enabled
            resp = client.chat.completions.create(
                model=model_name,
                messages=messages,
                tools=[{"type": "function", "function": f} for f in FUNCTION_SCHEMAS],
                tool_choice="auto",
                temperature=0.2,
                max_tokens=600,
            )

            choice = resp.choices[0]
            msg = choice.message
            actions: List[str] = []

            if msg.tool_calls:
                # Append the assistant tool-call message
                messages.append({
                    "role": "assistant",
                    "content": msg.content,
                    "tool_calls": [tc.model_dump() for tc in msg.tool_calls],
                })

                for tc in msg.tool_calls:
                    name = tc.function.name
                    args = json.loads(tc.function.arguments or "{}")
                    result, _ = execute_function(name, args)
                    actions.append(f"{name}: {result}")
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tc.id,
                        "name": name,
                        "content": json.dumps(result),
                    })

                # Second pass to get final answer with tool results
                followup = client.chat.completions.create(
                    model=model_name,
                    messages=messages,
                    temperature=0.2,
                    max_tokens=600,
                )
                final_msg = followup.choices[0].message
                return {
                    "reply": final_msg.content or "(empty reply)",
                    "model": model_name,
                    "actions": actions,
                }

            # No tool calls; return first-pass content
            return {
                "reply": msg.content or "(empty reply)",
                "model": model_name,
                "actions": actions,
            }
        except Exception as e:
            # Log the raw exception and stack to diagnose SDK/env issues
            import traceback
            traceback.print_exc()
            print(f"LLM OpenAI error: {type(e).__name__}: {e}")
            return {"reply": f"LLM call failed: {e}", "model": model_name}

    # Anthropic path
    if model_name.lower().startswith("claude"):
        try:
            import anthropic  # type: ignore
        except Exception:
            return {"reply": "LLM unavailable (Anthropic SDK not installed).", "model": model_name}

        if not settings.anthropic_api_key:
            return {"reply": "LLM unavailable (missing ANTHROPIC_API_KEY).", "model": model_name}

        try:
            client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
            # First pass with tool calling
            tool_defs = [
                {
                    "name": f["name"],
                    "description": f.get("description", ""),
                    "input_schema": f.get("parameters", {}),
                }
                for f in FUNCTION_SCHEMAS
            ]

            resp = client.messages.create(
                model=model_name,
                max_tokens=700,
                temperature=0.2,
                tools=tool_defs,
                messages=messages,
            )

            actions: List[str] = []

            if resp.stop_reason == "tool_use":
                # Collect tool uses
                tool_uses = [c for c in resp.content if c.type == "tool_use"]
                messages.append({
                    "role": "assistant",
                    "content": resp.content,
                })

                for tu in tool_uses:
                    name = tu.name
                    args = tu.input or {}
                    result, _ = execute_function(name, args)
                    actions.append(f"{name}: {result}")
                    messages.append({
                        "role": "tool",
                        "name": name,
                        "tool_call_id": tu.id,
                        "content": json.dumps(result),
                    })

                # Follow-up to get final answer
                follow = client.messages.create(
                    model=model_name,
                    max_tokens=700,
                    temperature=0.2,
                    tools=tool_defs,
                    messages=messages,
                )
                final_texts = [c.text for c in follow.content if hasattr(c, "text")]
                return {
                    "reply": final_texts[0] if final_texts else "(empty reply)",
                    "model": model_name,
                    "actions": actions,
                }

            # No tool calls
            texts = [c.text for c in resp.content if hasattr(c, "text")]
            return {
                "reply": texts[0] if texts else "(empty reply)",
                "model": model_name,
                "actions": actions,
            }
        except Exception as e:
            return {"reply": f"LLM call failed: {e}", "model": model_name}

    # Fallback
    return {"reply": "LLM model not recognized. Set MODEL_NAME to gpt-* or claude-*.", "model": model_name}


def build_retrieval_context(query: str, top_k: int = 4) -> Tuple[str, List[str]]:
    """Run semantic search and return context + source list."""
    retriever = get_retriever()
    if not retriever or not retriever.collections:
        return "", []

    results_by_collection = retriever.search_all(query=query, top_k=top_k)

    flattened: List[Dict] = []
    for coll, items in results_by_collection.items():
        for item in items:
            flattened.append({**item, "collection": coll})

    if not flattened:
        return "", []

    flattened.sort(key=lambda r: r.get("similarity", 0), reverse=True)

    context_chunks = []
    sources: List[str] = []
    for hit in flattened[:top_k]:
        meta = hit.get("metadata", {}) or {}
        source = meta.get("source_file") or meta.get("document_type") or hit.get("collection", "unknown")
        sources.append(str(source))
        preview = hit.get("content", "")
        context_chunks.append(
            f"[Collection: {hit.get('collection', 'n/a')} | Source: {source} | Sim: {hit.get('similarity', 0):.3f}]\n{preview}"
        )

    return "\n\n".join(context_chunks), list(dict.fromkeys(sources))  # dedupe sources, preserve order


@app.get("/health")
@limiter.limit("60/minute")
def health_check(request: Request):
    return {"status": "ok", "version": "0.2.0"}


@app.post("/api/auth/login", response_model=LoginResponse)
@limiter.limit("10/minute")
def login(request: Request, payload: LoginRequest):
    """Authenticate student and return JWT token with profile."""
    student = authenticate_student(payload.student_id, payload.password)
    
    if not student:
        return LoginResponse(
            success=False,
            message="Invalid student_id or password"
        )
    
    # Get full profile with courses and attendance
    profile = get_student_profile(payload.student_id)
    
    if not profile.get("found"):
        return LoginResponse(
            success=False,
            message="Could not fetch student profile"
        )
    
    # Generate JWT token
    token = create_jwt_token(
        student_id=payload.student_id,
        extra_data={"name": student["name"], "department": student["department"]}
    )
    
    return LoginResponse(
        success=True,
        token=token,
        profile=profile,
        message=f"Welcome, {student['name']}!"
    )


@app.get("/api/student/profile")
@limiter.limit("100/minute")
def get_profile(request: Request, student_id: Optional[str] = Depends(get_current_student)):
    """Get current student's profile (requires authentication)."""
    if not student_id:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    profile = get_student_profile(student_id)
    if not profile.get("found"):
        raise HTTPException(status_code=404, detail="Profile not found")
    
    return profile


@app.get("/api/chat/history")
@limiter.limit("100/minute")
def get_chat_history(
    request: Request,
    limit: int = 20,
    offset: int = 0,
    student_id: Optional[str] = Depends(get_current_student)
):
    """Get conversation history for authenticated student."""
    if not student_id:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    conversations = get_conversation_history(student_id, limit=limit, offset=offset)
    return {
        "student_id": student_id,
        "count": len(conversations),
        "conversations": conversations
    }


@app.post("/api/chat/feedback", response_model=FeedbackResponse)
@limiter.limit("50/minute")
def submit_feedback(
    request: Request,
    payload: FeedbackRequest,
    student_id: Optional[str] = Depends(get_current_student)
):
    """Submit feedback (thumbs up/down) for a conversation."""
    if not student_id:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    if payload.rating not in {1, -1}:
        raise HTTPException(status_code=400, detail="Rating must be 1 (thumbs up) or -1 (thumbs down)")
    
    try:
        feedback_id = save_feedback(
            conversation_id=payload.conversation_id,
            student_id=student_id,
            rating=payload.rating,
            comment=payload.comment
        )
        
        rating_text = "👍 positive" if payload.rating == 1 else "👎 negative"
        return FeedbackResponse(
            success=True,
            feedback_id=feedback_id,
            message=f"Thank you for your {rating_text} feedback!"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/analytics")
@limiter.limit("30/minute")
def get_analytics(request: Request, student_id: Optional[str] = Depends(get_current_student)):
    """Get analytics: most asked questions and conversation stats."""
    # Global analytics (no auth required for demo, but can be restricted)
    most_asked = get_most_asked_questions(limit=10, days=30)
    global_stats = get_conversation_stats()
    recent_feedback = get_recent_feedback(limit=5)
    
    result = {
        "most_asked_questions": most_asked,
        "global_stats": global_stats,
        "recent_feedback": recent_feedback
    }
    
    # Add student-specific stats if authenticated
    if student_id:
        student_stats = get_conversation_stats(student_id=student_id)
        result["student_stats"] = student_stats
    
    return result


@app.get("/api/student/attendance")
@limiter.limit("100/minute")
def get_student_attendance(
    request: Request,
    course_id: Optional[str] = Query(None, description="Filter by course_id"),
    student_id: Optional[str] = Depends(get_current_student)
):
    """Get attendance records for authenticated student."""
    if not student_id:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    from utils.automation import check_attendance
    import sqlite3
    from pathlib import Path
    
    # If specific course requested, return that record
    if course_id:
        result = check_attendance(student_id, course_id)
        return result
    
    # Otherwise, return all attendance records
    db_path = Path("data/database/college.db")
    if not db_path.exists():
        raise HTTPException(status_code=500, detail="Database not found")
    
    conn = sqlite3.connect(db_path, check_same_thread=False)
    try:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT a.course_id, c.course_name, a.total_classes, a.attended, a.percentage
            FROM attendance a
            JOIN courses c ON a.course_id = c.course_id
            WHERE a.student_id = ?
            ORDER BY a.percentage ASC
            """,
            (student_id,)
        )
        rows = cur.fetchall()
    finally:
        conn.close()
    
    records = []
    for course_id, course_name, total, attended, pct in rows:
        records.append({
            "course_id": course_id,
            "course_name": course_name,
            "total_classes": total,
            "attended": attended,
            "percentage": pct,
            "alert": pct < 75.0
        })
    
    return {
        "student_id": student_id,
        "count": len(records),
        "attendance": records
    }


@app.get("/api/student/schedule")
@limiter.limit("100/minute")
def get_student_schedule(
    request: Request,
    date: Optional[str] = Query(None, description="Date in YYYY-MM-DD format"),
    student_id: Optional[str] = Depends(get_current_student)
):
    """Get class schedule for authenticated student on a specific date."""
    if not student_id:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    from utils.automation import get_today_schedule
    
    result = get_today_schedule(student_id, target_date=date)
    return result


@app.get("/api/student/fees")
@limiter.limit("100/minute")
def get_student_fees(request: Request, student_id: Optional[str] = Depends(get_current_student)):
    """Get fee status for authenticated student."""
    if not student_id:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    from utils.automation import check_fee_status
    
    result = check_fee_status(student_id)
    if not result.get("found"):
        raise HTTPException(status_code=404, detail="No fee records found")
    
    return result


@app.post("/api/student/appointment")
@limiter.limit("20/minute")
def book_appointment(
    request: Request,
    payload: AppointmentRequest,
    student_id: Optional[str] = Depends(get_current_student)
):
    """Book faculty appointment for authenticated student."""
    if not student_id:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    from utils.automation import book_faculty_appointment
    
    result = book_faculty_appointment(
        student_id=student_id,
        faculty_id=payload.faculty_id,
        date=payload.date,
        time_slot=payload.time_slot
    )
    
    if not result.get("ok"):
        raise HTTPException(status_code=400, detail=result.get("message"))
    
    return result


@app.post("/api/student/leave")
@limiter.limit("20/minute")
def apply_leave(
    request: Request,
    payload: LeaveRequest,
    student_id: Optional[str] = Depends(get_current_student)
):
    """Apply for leave for authenticated student."""
    if not student_id:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    from utils.automation import apply_for_leave
    
    result = apply_for_leave(
        student_id=student_id,
        from_date=payload.from_date,
        to_date=payload.to_date,
        reason=payload.reason
    )
    
    return result


@app.post("/api/upload")
@limiter.limit("10/minute")
async def upload_file(
    request: Request,
    file: UploadFile = File(...),
    student_id: Optional[str] = Depends(get_current_student)
):
    """Upload a document (for leave applications, etc.). Requires authentication."""
    if not student_id:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    # Validate file type
    allowed_extensions = {".pdf", ".jpg", ".jpeg", ".png", ".doc", ".docx"}
    file_ext = Path(file.filename).suffix.lower()
    
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"File type not allowed. Allowed types: {', '.join(allowed_extensions)}"
        )
    
    # Generate unique filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_filename = f"{student_id}_{timestamp}_{file.filename}"
    file_path = UPLOAD_DIR / safe_filename
    
    # Save file
    try:
        content = await file.read()
        file_size = len(content)
        
        # Limit file size to 5MB
        if file_size > 5 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="File size exceeds 5MB limit")
        
        with open(file_path, "wb") as f:
            f.write(content)
        
        return UploadResponse(
            success=True,
            filename=safe_filename,
            filepath=str(file_path),
            size=file_size,
            message=f"File uploaded successfully: {safe_filename}"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@app.post("/api/chat", response_model=ChatResponse)
@limiter.limit("50/minute")
def chat(request: Request, payload: ChatRequest, student_id: Optional[str] = Depends(get_current_student)):
    """Chat endpoint with optional authentication for personalized responses."""
    if not payload.messages:
        raise HTTPException(status_code=400, detail="messages cannot be empty")

    user_query = payload.messages[-1].content
    
    # If authenticated, fetch student profile for personalization
    student_profile = None
    if student_id:
        profile_data = get_student_profile(student_id)
        if profile_data.get("found"):
            student_profile = profile_data
            # Auto-personalize queries
            user_query = personalize_query(user_query, student_id, student_profile)

    # Build context string for system prompt
    if student_profile:
        student_context = (
            f"Logged in as: {student_profile['name']} ({student_id}), "
            f"{student_profile['department']}, Year {student_profile['year']}. "
            f"Enrolled in {len(student_profile['enrolled_courses'])} courses."
        )
    else:
        student_context = payload.student_context

    system_prompt = build_system_prompt(
        college_name="[College Name]",
        student_context=student_context,
    )

    # Retrieval: semantic search with metadata preserved
    context_text, sources = build_retrieval_context(query=user_query, top_k=4)
    context_block = "Context:\n" + context_text if context_text else "Context: (no documents found)"

    # Assemble conversation with system prompt, context, and history
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "system", "content": context_block},
    ]
    messages.extend({"role": m.role, "content": m.content} for m in payload.messages)

    llm_result = call_llm(messages=messages, model_name=settings.model_name)

    # Save conversation to history if student is authenticated
    if student_id:
        try:
            conversation_id = save_conversation(
                student_id=student_id,
                user_query=payload.messages[-1].content,
                assistant_reply=llm_result.get("reply", ""),
                sources=sources,
                actions=llm_result.get("actions", []),
                model=llm_result.get("model")
            )
            # Optionally include conversation_id in response for feedback
            # (Not adding to ChatResponse model to keep it simple, but could be done)
        except Exception as e:
            # Log error but don't fail the request
            print(f"Warning: Failed to save conversation: {e}")

    return ChatResponse(
        reply=llm_result.get("reply", ""),
        sources=sources,
        actions=llm_result.get("actions", []),
        model=llm_result.get("model"),
    )


def personalize_query(query: str, student_id: str, profile: Dict) -> str:
    """Auto-inject student_id for personal queries like 'my schedule', 'my attendance'."""
    query_lower = query.lower()
    
    # Personal query patterns that should use logged-in student_id
    personal_patterns = [
        "my schedule", "my classes", "my courses",
        "my attendance", "my grades", "my fees",
        "my exams", "my profile"
    ]
    
    is_personal = any(pattern in query_lower for pattern in personal_patterns)
    
    if is_personal and student_id not in query:
        # Append student context
        query += f" (student_id: {student_id})"
    
    return query

