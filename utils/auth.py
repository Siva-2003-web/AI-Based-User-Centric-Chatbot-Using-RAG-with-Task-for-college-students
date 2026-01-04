"""Authentication utilities: JWT tokens, password hashing, login validation.

Features:
- Password hashing with bcrypt
- JWT token generation and verification
- Login validation against student database
"""

from __future__ import annotations

import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Optional, Any

import bcrypt
import jwt

DB_PATH = Path("data/database/college.db")

# JWT configuration (in production, use env vars and strong secrets)
JWT_SECRET = "college-assistant-secret-key-change-in-production"
JWT_ALGORITHM = "HS256"
JWT_EXPIRY_HOURS = 24


def _get_db_connection():
    """Create a new database connection (thread-safe)."""
    if not DB_PATH.exists():
        raise FileNotFoundError(f"Database not found at {DB_PATH}")
    return sqlite3.connect(DB_PATH, check_same_thread=False)


def hash_password(password: str) -> str:
    """Hash a password with bcrypt."""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def verify_password(password: str, hashed: str) -> bool:
    """Verify a password against a bcrypt hash."""
    return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))


def create_jwt_token(student_id: str, extra_data: Optional[Dict[str, Any]] = None) -> str:
    """Generate a JWT token for a student."""
    payload = {
        "student_id": student_id,
        "exp": datetime.utcnow() + timedelta(hours=JWT_EXPIRY_HOURS),
        "iat": datetime.utcnow(),
    }
    if extra_data:
        payload.update(extra_data)
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_jwt_token(token: str) -> Optional[Dict[str, Any]]:
    """Decode and verify a JWT token. Returns payload or None if invalid/expired."""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def authenticate_student(student_id: str, password: str) -> Optional[Dict[str, Any]]:
    """Validate student credentials and return student record if valid."""
    if not DB_PATH.exists():
        return None

    conn = _get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT student_id, name, department, year, email, phone, password_hash FROM students WHERE student_id = ? LIMIT 1",
            (student_id,),
        )
        row = cur.fetchone()
    finally:
        conn.close()

    if not row:
        return None

    stored_hash = row[6]  # password_hash column
    if not stored_hash or not verify_password(password, stored_hash):
        return None

    return {
        "student_id": row[0],
        "name": row[1],
        "department": row[2],
        "year": row[3],
        "email": row[4],
        "phone": row[5],
    }


def get_student_by_id(student_id: str) -> Optional[Dict[str, Any]]:
    """Fetch student record by ID (without password)."""
    if not DB_PATH.exists():
        return None

    conn = _get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT student_id, name, department, year, email, phone FROM students WHERE student_id = ? LIMIT 1",
            (student_id,),
        )
        row = cur.fetchone()
    finally:
        conn.close()

    if not row:
        return None

    return {
        "student_id": row[0],
        "name": row[1],
        "department": row[2],
        "year": row[3],
        "email": row[4],
        "phone": row[5],
    }
