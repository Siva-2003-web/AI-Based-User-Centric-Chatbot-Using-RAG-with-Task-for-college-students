"""Function schemas and executors for LLM function calling (OpenAI tools).

Includes:
- JSON schemas for OpenAI tool calling
- Dispatch to automation functions
- Student existence validation
- Basic slot availability helper for faculty appointments
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Tuple

from utils import automation
from utils.db import get_sqlite_pool

DB_PATH = Path("data/database/college.db")
POOL = get_sqlite_pool(DB_PATH)


def student_exists(student_id: str) -> bool:
    if not DB_PATH.exists():
        return False
    with POOL.connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT 1 FROM students WHERE student_id = ? LIMIT 1", (student_id,))
        found = cur.fetchone() is not None
    return found


def get_available_slots(faculty_id: str, date: str) -> List[str]:
    """Return simple availability: default slots minus existing appointments."""
    defaults = [
        "09:00-09:30",
        "10:00-10:30",
        "14:00-14:30",
        "16:00-16:30",
    ]
    if not DB_PATH.exists():
        return defaults

    with POOL.connection() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS appointments (
                appointment_id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id TEXT NOT NULL,
                faculty_id TEXT NOT NULL,
                date TEXT NOT NULL,
                time_slot TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'confirmed',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.commit()
        cur.execute(
            "SELECT time_slot FROM appointments WHERE faculty_id = ? AND date = ?",
            (faculty_id, date),
        )
        taken = {row[0] for row in cur.fetchall()}
    return [slot for slot in defaults if slot not in taken]


FUNCTION_SCHEMAS: List[Dict[str, Any]] = [
    {
        "name": "check_attendance",
        "description": "Check attendance percentage for a student in a course.",
        "parameters": {
            "type": "object",
            "properties": {
                "student_id": {"type": "string"},
                "course_id": {"type": "string"},
            },
            "required": ["student_id", "course_id"],
        },
    },
    {
        "name": "get_today_schedule",
        "description": "Get the student's schedule for a specific date (defaults to today).",
        "parameters": {
            "type": "object",
            "properties": {
                "student_id": {"type": "string"},
                "date": {"type": "string", "description": "ISO date (YYYY-MM-DD)"},
            },
            "required": ["student_id"],
        },
    },
    {
        "name": "check_fee_status",
        "description": "Check fee status for a student (latest record).",
        "parameters": {
            "type": "object",
            "properties": {
                "student_id": {"type": "string"},
            },
            "required": ["student_id"],
        },
    },
    {
        "name": "get_grades",
        "description": "Get grade and credits for a course in a given semester.",
        "parameters": {
            "type": "object",
            "properties": {
                "student_id": {"type": "string"},
                "course_id": {"type": "string"},
                "semester": {"type": "string"},
            },
            "required": ["student_id", "course_id", "semester"],
        },
    },
    {
        "name": "get_exam_schedule",
        "description": "List upcoming exams for a student in a semester.",
        "parameters": {
            "type": "object",
            "properties": {
                "student_id": {"type": "string"},
                "semester": {"type": "string"},
            },
            "required": ["student_id", "semester"],
        },
    },
    {
        "name": "book_faculty_appointment",
        "description": "Book a faculty appointment given faculty_id, date, and time_slot.",
        "parameters": {
            "type": "object",
            "properties": {
                "student_id": {"type": "string"},
                "faculty_id": {"type": "string"},
                "date": {"type": "string", "description": "ISO date"},
                "time_slot": {"type": "string", "description": "e.g., 14:00-14:30"},
            },
            "required": ["student_id", "faculty_id", "date", "time_slot"],
        },
    },
    {
        "name": "apply_for_leave",
        "description": "Submit a leave request for a date range with reason.",
        "parameters": {
            "type": "object",
            "properties": {
                "student_id": {"type": "string"},
                "from_date": {"type": "string"},
                "to_date": {"type": "string"},
                "reason": {"type": "string"},
            },
            "required": ["student_id", "from_date", "to_date", "reason"],
        },
    },
    {
        "name": "request_document",
        "description": "Request official documents (Bonafide, ID Card, Transcript, NOC).",
        "parameters": {
            "type": "object",
            "properties": {
                "student_id": {"type": "string"},
                "document_type": {"type": "string"},
            },
            "required": ["student_id", "document_type"],
        },
    },
]


def execute_function(name: str, args: Dict[str, Any]) -> Tuple[Dict[str, Any], List[str]]:
    """Execute a function by name with validation. Returns (result, actions)."""
    actions: List[str] = []

    # Student validation where applicable
    if "student_id" in args:
        if not student_exists(args["student_id"]):
            return {"ok": False, "message": "Invalid student_id"}, actions

    try:
        if name == "check_attendance":
            return automation.check_attendance(args["student_id"], args["course_id"]), actions
        if name == "get_today_schedule":
            return automation.get_today_schedule(args["student_id"], args.get("date")), actions
        if name == "check_fee_status":
            return automation.check_fee_status(args["student_id"]), actions
        if name == "get_grades":
            return automation.get_grades(args["student_id"], args["course_id"], args["semester"]), actions
        if name == "get_exam_schedule":
            return automation.get_exam_schedule(args["student_id"], args["semester"]), actions
        if name == "book_faculty_appointment":
            # Provide availability helper for confirmation flows
            available = get_available_slots(args["faculty_id"], args["date"])
            if args.get("time_slot") not in available:
                return {
                    "ok": False,
                    "message": "Slot unavailable or not provided.",
                    "available_slots": available,
                }, actions
            return automation.book_faculty_appointment(
                args["student_id"], args["faculty_id"], args["date"], args["time_slot"]
            ), actions
        if name == "apply_for_leave":
            return automation.apply_for_leave(args["student_id"], args["from_date"], args["to_date"], args["reason"]), actions
        if name == "request_document":
            return automation.request_document(args["student_id"], args["document_type"]), actions
    except Exception as e:
        return {"ok": False, "message": f"Function execution error: {e}"}, actions

    return {"ok": False, "message": f"Unknown function: {name}"}, actions
