"""College-specific automation functions with notification stubs.

Functions:
- check_attendance(student_id, course_id)
- get_today_schedule(student_id, date)
- check_fee_status(student_id)
- get_grades(student_id, course_id, semester)
- book_faculty_appointment(student_id, faculty_id, date, time_slot)
- apply_for_leave(student_id, from_date, to_date, reason)
- get_exam_schedule(student_id, semester)
- request_document(student_id, document_type)

Data sources:
- SQLite DB: data/database/college.db (attendance, enrollments, courses, faculty, exams, fees)
- Course catalog CSV: data/catalogs/course_catalog_2025_2026.csv (meeting_times, instructor)
"""

from __future__ import annotations

import csv
import sqlite3
from datetime import date as date_cls
from pathlib import Path
from typing import Any, Dict, List

from utils import notifications

DB_PATH = Path("data/database/college.db")
CATALOG_PATH = Path("data/catalogs/course_catalog_2025_2026.csv")


def _get_conn():
    """Create a new database connection (thread-safe for FastAPI)."""
    if not DB_PATH.exists():
        raise FileNotFoundError(f"Database not found at {DB_PATH}")
    return sqlite3.connect(DB_PATH, check_same_thread=False)


def _load_catalog_meeting_times() -> Dict[str, Dict[str, str]]:
    catalog: Dict[str, Dict[str, str]] = {}
    if not CATALOG_PATH.exists():
        return catalog
    with open(CATALOG_PATH, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            code = row.get("course_code") or row.get("course_id")
            if not code:
                continue
            catalog[code.strip()] = {
                "meeting_times": row.get("meeting_times", ""),
                "catalog_instructor": row.get("instructor", ""),
            }
    return catalog


def _get_student_contact(student_id: str) -> Dict[str, str]:
    conn = _get_conn()
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT name, email, phone FROM students WHERE student_id = ? LIMIT 1",
            (student_id,),
        )
        row = cur.fetchone()
    finally:
        conn.close()
    if not row:
        return {}
    return {"name": row[0], "email": row[1], "phone": row[2]}


def check_attendance(student_id: str, course_id: str) -> Dict[str, Any]:
    """Return attendance summary and alert flag for a student in a course."""
    conn = _get_conn()
    try:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT a.total_classes, a.attended, a.percentage, c.course_name
            FROM attendance a
            JOIN courses c ON a.course_id = c.course_id
            WHERE a.student_id = ? AND a.course_id = ?
            """,
            (student_id, course_id),
        )
        row = cur.fetchone()
    finally:
        conn.close()

    if not row:
        return {
            "found": False,
            "message": f"No attendance record for {student_id} in {course_id}.",
        }

    total_classes, attended, percentage, course_name = row
    alert = percentage < 75.0
    message = f"Your attendance in {course_name}: {percentage:.0f}% ({attended}/{total_classes} classes)"
    if alert:
        message += " — below 75% threshold."

    return {
        "found": True,
        "student_id": student_id,
        "course_id": course_id,
        "course_name": course_name,
        "total_classes": total_classes,
        "attended": attended,
        "percentage": percentage,
        "alert": alert,
        "message": message,
    }


def get_today_schedule(student_id: str, target_date: str | None = None) -> Dict[str, Any]:
    """Return classes for a student on a given date (uses catalog meeting_times as schedule)."""
    conn = _get_conn()
    try:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT e.course_id, c.course_name, c.department, c.semester, f.name AS faculty_name
            FROM enrollments e
            JOIN courses c ON e.course_id = c.course_id
            JOIN faculty f ON c.faculty_id = f.faculty_id
            WHERE e.student_id = ?
            """,
            (student_id,),
        )
        rows = cur.fetchall()

    finally:
        conn.close()
    catalog = _load_catalog_meeting_times()
    today = target_date or date_cls.today().isoformat()

    schedule: List[Dict[str, Any]] = []
    for course_id, course_name, department, semester, faculty_name in rows:
        cat = catalog.get(course_id, {})
        meeting_times = cat.get("meeting_times", "")
        catalog_instructor = cat.get("catalog_instructor", "")
        schedule.append({
            "course_id": course_id,
            "course_name": course_name,
            "department": department,
            "semester": semester,
            "date": today,
            "meeting_times": meeting_times or "Time not listed",
            "faculty_name": faculty_name,
            "catalog_instructor": catalog_instructor,
        })

    return {
        "student_id": student_id,
        "date": today,
        "count": len(schedule),
        "classes": schedule,
        "message": f"Schedule for {student_id} on {today}: {len(schedule)} class(es)",
    }


def check_fee_status(student_id: str) -> Dict[str, Any]:
    """Return fee status for a student (latest record)."""
    conn = _get_conn()
    try:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT total_fees, paid_amount, due_amount, due_date, status, semester
            FROM fees
            WHERE student_id = ?
            ORDER BY created_at DESC
            LIMIT 1
            """,
            (student_id,),
        )
        row = cur.fetchone()

    finally:
        conn.close()
    if not row:
        return {"found": False, "message": f"No fee record for {student_id}."}

    total, paid, due, due_date, status, semester = row
    message = f"Fees for {semester}: total {total:.2f}, paid {paid:.2f}, due {due:.2f}, due date {due_date} (status: {status})."
    return {
        "found": True,
        "student_id": student_id,
        "total": total,
        "paid": paid,
        "due": due,
        "due_date": due_date,
        "status": status,
        "semester": semester,
        "message": message,
    }


def get_grades(student_id: str, course_id: str, semester: str) -> Dict[str, Any]:
    """Return grade and credits for a student/course/semester using enrollments + courses."""
    conn = _get_conn()
    try:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT e.grade, c.credits, c.course_name
            FROM enrollments e
            JOIN courses c ON e.course_id = c.course_id
            WHERE e.student_id = ? AND e.course_id = ? AND e.semester = ?
            """,
            (student_id, course_id, semester),
        )
        row = cur.fetchone()

    finally:
        conn.close()
    if not row:
        return {"found": False, "message": f"No grade found for {student_id} in {course_id} ({semester})."}

    grade, credits, course_name = row
    message = f"Grade for {course_name} ({semester}): {grade or 'N/A'} | Credits: {credits}"
    return {
        "found": True,
        "student_id": student_id,
        "course_id": course_id,
        "course_name": course_name,
        "semester": semester,
        "grade": grade,
        "credits": credits,
        "message": message,
    }


def book_faculty_appointment(student_id: str, faculty_id: str, date: str, time_slot: str) -> Dict[str, Any]:
    """Book a faculty appointment if the slot is free; persist record and confirm."""
    conn = _get_conn()
    try:
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
            """
            SELECT 1 FROM appointments
            WHERE faculty_id = ? AND date = ? AND time_slot = ?
            LIMIT 1
            """,
            (faculty_id, date, time_slot),
        )
        if cur.fetchone():
            return {"ok": False, "message": "Slot unavailable; choose another time."}

        cur.execute(
            """
            INSERT INTO appointments (student_id, faculty_id, date, time_slot)
            VALUES (?, ?, ?, ?)
            """,
            (student_id, faculty_id, date, time_slot),
        )
        conn.commit()
        appt_id = cur.lastrowid

    finally:
        conn.close()
    contact = _get_student_contact(student_id)
    if contact.get("email"):
        faculty_name = faculty_id
        conn = _get_conn()
        try:
            cur = conn.cursor()
            cur.execute("SELECT name FROM faculty WHERE faculty_id = ?", (faculty_id,))
            row = cur.fetchone()
            if row:
                faculty_name = row[0]
        finally:
            conn.close()
        tpl = notifications.tpl_appointment_confirmation(contact.get("name", student_id), faculty_name, date, time_slot)
        notifications.send_email(contact["email"], tpl["subject"], tpl["body"])

    return {
        "ok": True,
        "appointment_id": appt_id,
        "student_id": student_id,
        "faculty_id": faculty_id,
        "date": date,
        "time_slot": time_slot,
        "message": f"Appointment confirmed for {date} at {time_slot} (ID: {appt_id}).",
    }


def apply_for_leave(student_id: str, from_date: str, to_date: str, reason: str) -> Dict[str, Any]:
    """Create a leave application record and return a ticket number."""
    conn = _get_conn()
    try:
        cur = conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS leave_applications (
                ticket_id TEXT PRIMARY KEY,
                student_id TEXT NOT NULL,
                from_date TEXT NOT NULL,
                to_date TEXT NOT NULL,
                reason TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'submitted',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.commit()

        ticket = f"LV-{student_id}-{from_date.replace('-', '')}-{to_date.replace('-', '')}"
        cur.execute(
            """
            INSERT OR REPLACE INTO leave_applications (ticket_id, student_id, from_date, to_date, reason)
            VALUES (?, ?, ?, ?, ?)
            """,
            (ticket, student_id, from_date, to_date, reason),
        )
        conn.commit()

    finally:
        conn.close()
    contact = _get_student_contact(student_id)
    if contact.get("email"):
        tpl = notifications.tpl_leave_status(contact.get("name", student_id), ticket, "submitted", from_date, to_date)
        notifications.send_email(contact["email"], tpl["subject"], tpl["body"])

    return {
        "ok": True,
        "ticket_id": ticket,
        "student_id": student_id,
        "from_date": from_date,
        "to_date": to_date,
        "reason": reason,
        "status": "submitted",
        "message": f"Leave request submitted. Ticket: {ticket}",
    }


def get_exam_schedule(student_id: str, semester: str) -> Dict[str, Any]:
    """Return upcoming exams for the student's enrolled courses in a semester."""
    conn = _get_conn()
    try:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT e.course_id
            FROM enrollments e
            WHERE e.student_id = ? AND e.semester = ?
            """,
            (student_id, semester),
        )
        course_ids = [row[0] for row in cur.fetchall()]

        if not course_ids:
            return {"found": False, "message": f"No enrollments for {student_id} in {semester}."}

        placeholders = ",".join("?" * len(course_ids))
        cur.execute(
            f"""
            SELECT ex.course_id, c.course_name, ex.exam_date, ex.exam_time, ex.room_number, ex.exam_type
            FROM exams ex
            JOIN courses c ON ex.course_id = c.course_id
            WHERE ex.course_id IN ({placeholders}) AND ex.semester = ?
            ORDER BY ex.exam_date, ex.exam_time
            """,
            (*course_ids, semester),
        )
        exams = cur.fetchall()

    finally:
        conn.close()
    if not exams:
        return {"found": False, "message": f"No exams scheduled for {semester}."}

    items: List[Dict[str, Any]] = []
    for course_id, course_name, exam_date, exam_time, room, exam_type in exams:
        items.append({
            "course_id": course_id,
            "course_name": course_name,
            "exam_date": exam_date,
            "exam_time": exam_time,
            "room": room,
            "exam_type": exam_type,
        })

    return {
        "found": True,
        "student_id": student_id,
        "semester": semester,
        "count": len(items),
        "exams": items,
        "message": f"Exams for {semester}: {len(items)} found",
    }


def request_document(student_id: str, document_type: str) -> Dict[str, Any]:
    """Create a document request ticket and return ETA."""
    allowed = {"Bonafide", "ID Card", "Transcript", "NOC"}
    if document_type not in allowed:
        return {"ok": False, "message": f"Unsupported document type. Choose from: {', '.join(sorted(allowed))}"}

    conn = _get_conn()
    try:
        cur = conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS document_requests (
                ticket_id TEXT PRIMARY KEY,
                student_id TEXT NOT NULL,
                document_type TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'submitted',
                eta_days INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.commit()

        eta = 2 if document_type in {"Bonafide", "ID Card"} else 5
        ticket = f"DOC-{student_id}-{document_type.replace(' ', '').upper()}"

        cur.execute(
            """
            INSERT OR REPLACE INTO document_requests (ticket_id, student_id, document_type, eta_days)
            VALUES (?, ?, ?, ?)
            """,
            (ticket, student_id, document_type, eta),
        )
        conn.commit()

    finally:
        conn.close()
    contact = _get_student_contact(student_id)
    if contact.get("email"):
        subject = "Document Request Submitted"
        body = (
            f"Hello {contact.get('name', student_id)},\n\n"
            f"Your request for {document_type} is submitted. Ticket: {ticket}. ETA: {eta} day(s).\n\nRegards,\nCollege Office"
        )
        notifications.send_email(contact["email"], subject, body)

    return {
        "ok": True,
        "ticket_id": ticket,
        "student_id": student_id,
        "document_type": document_type,
        "eta_days": eta,
        "status": "submitted",
        "message": f"Request submitted. Ticket: {ticket}. Estimated completion: {eta} day(s).",
    }


def get_student_profile(student_id: str) -> Dict[str, Any]:
    """Fetch complete student profile with enrolled courses and attendance summary."""
    conn = _get_conn()
    try:
        cur = conn.cursor()
        
        # Basic student info
        cur.execute(
            "SELECT student_id, name, department, year, email, phone FROM students WHERE student_id = ? LIMIT 1",
            (student_id,),
        )
        student_row = cur.fetchone()
        
        if not student_row:
            return {"found": False, "message": f"Student {student_id} not found."}
        
        # Enrolled courses
        cur.execute(
            """
            SELECT e.course_id, c.course_name, c.credits, e.semester, e.grade
            FROM enrollments e
            JOIN courses c ON e.course_id = c.course_id
            WHERE e.student_id = ?
            ORDER BY e.semester DESC
            """,
            (student_id,),
        )
        enrollments = cur.fetchall()
        
        # Attendance summary across all courses
        cur.execute(
            """
            SELECT a.course_id, c.course_name, a.total_classes, a.attended, a.percentage
            FROM attendance a
            JOIN courses c ON a.course_id = c.course_id
            WHERE a.student_id = ?
            """,
            (student_id,),
        )
        attendance_rows = cur.fetchall()
    
    finally:
        conn.close()
    
    enrolled_courses: List[Dict[str, Any]] = []
    for course_id, course_name, credits, semester, grade in enrollments:
        enrolled_courses.append({
            "course_id": course_id,
            "course_name": course_name,
            "credits": credits,
            "semester": semester,
            "grade": grade or "In Progress",
        })
    
    attendance_summary: List[Dict[str, Any]] = []
    for course_id, course_name, total_classes, attended, percentage in attendance_rows:
        attendance_summary.append({
            "course_id": course_id,
            "course_name": course_name,
            "total_classes": total_classes,
            "attended": attended,
            "percentage": percentage,
            "alert": percentage < 75.0,
        })
    
    return {
        "found": True,
        "student_id": student_row[0],
        "name": student_row[1],
        "department": student_row[2],
        "year": student_row[3],
        "email": student_row[4],
        "phone": student_row[5],
        "enrolled_courses": enrolled_courses,
        "attendance_summary": attendance_summary,
        "message": f"Profile for {student_row[1]} ({student_id})",
    }


if __name__ == "__main__":
    # Simple manual test harness
    print(check_attendance("STU00001", "CS101"))
    print(get_today_schedule("STU00001"))
    print(check_fee_status("STU00001"))
    print(get_grades("STU00001", "CS101", "Fall 2025"))
    print(book_faculty_appointment("STU00001", "F001", "2026-01-05", "10:00-10:30"))
    print(apply_for_leave("STU00001", "2026-01-10", "2026-01-12", "Medical"))
    print(get_exam_schedule("STU00001", "Fall 2025"))
    print(request_document("STU00001", "Bonafide"))
