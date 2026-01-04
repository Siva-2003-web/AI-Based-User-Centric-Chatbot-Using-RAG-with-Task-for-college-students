"""Notification utilities (email/SMS stubs) with templates.

This module is intentionally lightweight: it logs payloads instead of
sending real messages. Wire to SMTP/SendGrid/Twilio by replacing the
`send_email`/`send_sms` implementations.
"""

from __future__ import annotations

from typing import Dict


def send_email(to: str, subject: str, body: str, provider: str = "smtp") -> Dict[str, str]:
    # Stub implementation: replace with SMTP/SendGrid client as needed.
    print(f"[email:{provider}] to={to} subject={subject}\n{body}\n")
    return {"ok": True, "provider": provider, "to": to, "subject": subject}


def send_sms(to: str, body: str, provider: str = "twilio") -> Dict[str, str]:
    # Stub implementation: replace with Twilio/etc.
    print(f"[sms:{provider}] to={to}\n{body}\n")
    return {"ok": True, "provider": provider, "to": to}


# Templates

def tpl_appointment_confirmation(student_name: str, faculty_name: str, date: str, time_slot: str) -> Dict[str, str]:
    subject = "Appointment Confirmed"
    body = f"Hello {student_name},\n\nYour appointment with {faculty_name} is confirmed for {date} at {time_slot}.\n\nRegards,\nCollege Office"
    return {"subject": subject, "body": body}


def tpl_leave_status(student_name: str, ticket: str, status: str, from_date: str, to_date: str) -> Dict[str, str]:
    subject = "Leave Application Status"
    body = (
        f"Hello {student_name},\n\nYour leave request {ticket} is {status}.\n"
        f"Dates: {from_date} to {to_date}.\n\nRegards,\nCollege Office"
    )
    return {"subject": subject, "body": body}


def tpl_fee_reminder(student_name: str, due: float, due_date: str) -> Dict[str, str]:
    subject = "Fee Payment Reminder"
    body = (
        f"Hello {student_name},\n\nYour outstanding fee is {due:.2f}. Due date: {due_date}."
        "\nPlease ignore if already paid.\n\nRegards,\nFinance Office"
    )
    return {"subject": subject, "body": body}


def tpl_exam_alert(student_name: str, course_name: str, date: str, time: str, room: str) -> Dict[str, str]:
    subject = "Upcoming Exam Reminder"
    body = (
        f"Hello {student_name},\n\nExam for {course_name}: {date} at {time}, Room {room}."
        "\nGood luck!\n\nRegards,\nExams Office"
    )
    return {"subject": subject, "body": body}
