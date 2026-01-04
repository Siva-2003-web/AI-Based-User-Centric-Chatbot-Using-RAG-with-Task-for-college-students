"""Conversation history and feedback utilities.

Features:
- Save and retrieve conversation history per student
- Track feedback (thumbs up/down)
- Analytics for most asked questions
"""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any

DB_PATH = Path("data/database/college.db")


def _get_db_connection():
    """Create a new database connection (thread-safe)."""
    if not DB_PATH.exists():
        raise FileNotFoundError(f"Database not found at {DB_PATH}")
    return sqlite3.connect(DB_PATH, check_same_thread=False)


def save_conversation(
    student_id: str,
    user_query: str,
    assistant_reply: str,
    sources: Optional[List[str]] = None,
    actions: Optional[List[str]] = None,
    model: Optional[str] = None
) -> int:
    """Save a conversation to history. Returns conversation_id."""
    conn = _get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO conversation_history 
            (student_id, user_query, assistant_reply, sources, actions, model, created_at)
            VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """,
            (
                student_id,
                user_query,
                assistant_reply,
                json.dumps(sources) if sources else None,
                json.dumps(actions) if actions else None,
                model
            )
        )
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()


def get_conversation_history(
    student_id: str,
    limit: int = 20,
    offset: int = 0
) -> List[Dict[str, Any]]:
    """Retrieve conversation history for a student."""
    conn = _get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT 
                conversation_id, user_query, assistant_reply, sources, actions, model, created_at
            FROM conversation_history
            WHERE student_id = ?
            ORDER BY created_at DESC
            LIMIT ? OFFSET ?
            """,
            (student_id, limit, offset)
        )
        rows = cur.fetchall()
    finally:
        conn.close()
    
    conversations: List[Dict[str, Any]] = []
    for row in rows:
        conversations.append({
            "conversation_id": row[0],
            "user_query": row[1],
            "assistant_reply": row[2],
            "sources": json.loads(row[3]) if row[3] else [],
            "actions": json.loads(row[4]) if row[4] else [],
            "model": row[5],
            "created_at": row[6]
        })
    
    return conversations


def save_feedback(
    conversation_id: int,
    student_id: str,
    rating: int,
    comment: Optional[str] = None
) -> int:
    """Save feedback for a conversation. Rating: 1=👍, -1=👎. Returns feedback_id."""
    if rating not in {1, -1}:
        raise ValueError("Rating must be 1 (thumbs up) or -1 (thumbs down)")
    
    conn = _get_db_connection()
    try:
        cur = conn.cursor()
        # Check if feedback already exists for this conversation
        cur.execute(
            "SELECT feedback_id FROM feedback WHERE conversation_id = ? AND student_id = ?",
            (conversation_id, student_id)
        )
        existing = cur.fetchone()
        
        if existing:
            # Update existing feedback
            cur.execute(
                """
                UPDATE feedback 
                SET rating = ?, comment = ?, created_at = CURRENT_TIMESTAMP
                WHERE feedback_id = ?
                """,
                (rating, comment, existing[0])
            )
            conn.commit()
            return existing[0]
        else:
            # Insert new feedback
            cur.execute(
                """
                INSERT INTO feedback (conversation_id, student_id, rating, comment)
                VALUES (?, ?, ?, ?)
                """,
                (conversation_id, student_id, rating, comment)
            )
            conn.commit()
            return cur.lastrowid
    finally:
        conn.close()


def get_most_asked_questions(limit: int = 10, days: int = 30) -> List[Dict[str, Any]]:
    """Get most frequently asked questions in the last N days."""
    conn = _get_db_connection()
    try:
        cur = conn.cursor()
        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
        
        cur.execute(
            """
            SELECT 
                user_query,
                COUNT(*) as frequency,
                AVG(CASE WHEN f.rating IS NOT NULL THEN f.rating ELSE 0 END) as avg_rating
            FROM conversation_history ch
            LEFT JOIN feedback f ON ch.conversation_id = f.conversation_id
            WHERE ch.created_at >= ?
            GROUP BY LOWER(user_query)
            ORDER BY frequency DESC
            LIMIT ?
            """,
            (cutoff_date, limit)
        )
        rows = cur.fetchall()
    finally:
        conn.close()
    
    questions: List[Dict[str, Any]] = []
    for row in rows:
        questions.append({
            "question": row[0],
            "frequency": row[1],
            "avg_rating": round(row[2], 2) if row[2] else 0.0
        })
    
    return questions


def get_conversation_stats(student_id: Optional[str] = None) -> Dict[str, Any]:
    """Get conversation statistics (global or per student)."""
    conn = _get_db_connection()
    try:
        cur = conn.cursor()
        
        if student_id:
            # Student-specific stats
            cur.execute(
                """
                SELECT 
                    COUNT(*) as total_conversations,
                    COUNT(DISTINCT DATE(created_at)) as active_days,
                    AVG(LENGTH(user_query)) as avg_query_length
                FROM conversation_history
                WHERE student_id = ?
                """,
                (student_id,)
            )
            row = cur.fetchone()
            
            cur.execute(
                """
                SELECT COUNT(*) as positive_feedback
                FROM feedback f
                JOIN conversation_history ch ON f.conversation_id = ch.conversation_id
                WHERE ch.student_id = ? AND f.rating = 1
                """,
                (student_id,)
            )
            positive = cur.fetchone()[0]
            
            cur.execute(
                """
                SELECT COUNT(*) as negative_feedback
                FROM feedback f
                JOIN conversation_history ch ON f.conversation_id = ch.conversation_id
                WHERE ch.student_id = ? AND f.rating = -1
                """,
                (student_id,)
            )
            negative = cur.fetchone()[0]
        else:
            # Global stats
            cur.execute(
                """
                SELECT 
                    COUNT(*) as total_conversations,
                    COUNT(DISTINCT student_id) as unique_students,
                    AVG(LENGTH(user_query)) as avg_query_length
                FROM conversation_history
                """
            )
            row = cur.fetchone()
            
            cur.execute("SELECT COUNT(*) FROM feedback WHERE rating = 1")
            positive = cur.fetchone()[0]
            
            cur.execute("SELECT COUNT(*) FROM feedback WHERE rating = -1")
            negative = cur.fetchone()[0]
    finally:
        conn.close()
    
    stats = {
        "total_conversations": row[0] if row else 0,
        "positive_feedback": positive,
        "negative_feedback": negative,
        "feedback_ratio": round(positive / (positive + negative), 2) if (positive + negative) > 0 else 0.0
    }
    
    if student_id:
        stats["active_days"] = row[1] if row else 0
    else:
        stats["unique_students"] = row[1] if row else 0
    
    return stats


def get_recent_feedback(limit: int = 10) -> List[Dict[str, Any]]:
    """Get recent feedback with conversation details."""
    conn = _get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT 
                f.feedback_id,
                f.conversation_id,
                f.student_id,
                f.rating,
                f.comment,
                f.created_at,
                ch.user_query,
                ch.assistant_reply
            FROM feedback f
            JOIN conversation_history ch ON f.conversation_id = ch.conversation_id
            ORDER BY f.created_at DESC
            LIMIT ?
            """,
            (limit,)
        )
        rows = cur.fetchall()
    finally:
        conn.close()
    
    feedback_list: List[Dict[str, Any]] = []
    for row in rows:
        feedback_list.append({
            "feedback_id": row[0],
            "conversation_id": row[1],
            "student_id": row[2],
            "rating": "👍" if row[3] == 1 else "👎",
            "rating_value": row[3],
            "comment": row[4],
            "created_at": row[5],
            "user_query": row[6],
            "assistant_reply": row[7][:200] + "..." if len(row[7]) > 200 else row[7]
        })
    
    return feedback_list
