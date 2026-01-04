"""
Tool schemas for college assistant automation.
Each tool defines input parameters, validation, and execution scope.
"""

# 1. Course Recommendation Tool
COURSE_RECOMMENDATION_TOOL = {
    "name": "recommend_courses",
    "description": "Recommend courses based on student major, progress, and interests.",
    "input_schema": {
        "type": "object",
        "properties": {
            "student_id": {"type": "string", "description": "Student unique ID (authenticated)"},
            "major": {
                "type": "string",
                "description": "Student's major or degree program",
            },
            "completed_courses": {
                "type": "array",
                "items": {"type": "string"},
                "description": "List of course codes already completed",
            },
            "interests": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Optional tags (e.g., AI, biology, writing) for guided selection",
            },
            "semester": {
                "type": "string",
                "description": "Target semester (e.g., Spring 2026)",
            },
        },
        "required": ["student_id", "major", "semester"],
    },
    "output": {
        "type": "object",
        "properties": {
            "recommendations": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "course_code": {"type": "string"},
                        "title": {"type": "string"},
                        "reason": {"type": "string", "description": "Why recommended"},
                        "available_sections": {"type": "array"},
                    },
                },
            },
            "warnings": {
                "type": "array",
                "items": {"type": "string"},
                "description": "E.g., missing prerequisites, over-capacity",
            },
        },
    },
}

# 2. Schedule/Tutoring Booking Tool
SCHEDULE_MEETING_TOOL = {
    "name": "schedule_meeting",
    "description": "Schedule a meeting with advisor, tutor, or counselor.",
    "input_schema": {
        "type": "object",
        "properties": {
            "student_id": {"type": "string"},
            "meeting_type": {
                "type": "string",
                "enum": ["advising", "tutoring", "counseling", "career"],
                "description": "Type of meeting requested",
            },
            "preferred_times": {
                "type": "array",
                "items": {"type": "string"},
                "description": "ISO 8601 datetime slots (e.g., 2026-01-15T14:00:00Z)",
            },
            "topic": {
                "type": "string",
                "description": "Brief topic or course code (e.g., 'help with CS101 assignment')",
            },
            "duration_minutes": {"type": "integer", "default": 30},
        },
        "required": ["student_id", "meeting_type", "preferred_times"],
    },
    "output": {
        "type": "object",
        "properties": {
            "status": {
                "type": "string",
                "enum": ["scheduled", "pending_confirmation", "no_availability"],
            },
            "confirmed_time": {"type": "string", "description": "ISO 8601 if scheduled"},
            "calendar_link": {"type": "string", "description": "Google/O365 calendar event URL"},
            "assigned_staff": {"type": "object", "properties": {"name": {"type": "string"}, "email": {"type": "string"}}},
        },
    },
}

# 3. Send Notification/Reminder Tool
SEND_NOTIFICATION_TOOL = {
    "name": "send_notification",
    "description": "Send email, SMS, or in-app notification to student.",
    "input_schema": {
        "type": "object",
        "properties": {
            "recipient_id": {"type": "string", "description": "Student ID or staff email"},
            "channel": {
                "type": "string",
                "enum": ["email", "sms", "in_app", "slack"],
                "description": "Delivery method",
            },
            "subject": {"type": "string", "description": "For email"},
            "message": {"type": "string", "description": "Notification body"},
            "reminder_time": {
                "type": "string",
                "description": "ISO 8601 for scheduled sends (optional)",
            },
            "priority": {
                "type": "string",
                "enum": ["low", "normal", "high", "urgent"],
                "default": "normal",
            },
        },
        "required": ["recipient_id", "channel", "message"],
    },
    "output": {
        "type": "object",
        "properties": {
            "notification_id": {"type": "string"},
            "status": {"type": "string", "enum": ["sent", "queued", "failed"]},
            "timestamp": {"type": "string"},
        },
    },
}

# 4. Create Support Ticket Tool
CREATE_TICKET_TOOL = {
    "name": "create_ticket",
    "description": "Create a support or administrative ticket.",
    "input_schema": {
        "type": "object",
        "properties": {
            "student_id": {"type": "string"},
            "category": {
                "type": "string",
                "enum": ["registration", "billing", "housing", "academic_exception", "health_safety", "other"],
            },
            "title": {"type": "string"},
            "description": {"type": "string"},
            "priority": {
                "type": "string",
                "enum": ["low", "medium", "high", "critical"],
                "default": "medium",
            },
            "attachments": {
                "type": "array",
                "items": {"type": "string"},
                "description": "File paths or URLs",
            },
        },
        "required": ["student_id", "category", "title", "description"],
    },
    "output": {
        "type": "object",
        "properties": {
            "ticket_id": {"type": "string"},
            "status": {"type": "string", "enum": ["open", "assigned", "in_progress", "resolved"]},
            "assigned_to": {"type": "string"},
            "created_at": {"type": "string"},
        },
    },
}

# 5. Retrieve Student Records Tool (Restricted)
GET_STUDENT_RECORD_TOOL = {
    "name": "get_student_record",
    "description": "Fetch authenticated student's own record (schedule, grades, degree progress, holds).",
    "input_schema": {
        "type": "object",
        "properties": {
            "student_id": {"type": "string", "description": "From JWT/auth context"},
            "record_type": {
                "type": "string",
                "enum": ["schedule", "grades", "degree_progress", "financial_holds", "transcript"],
            },
            "term": {"type": "string", "description": "Optional: Spring 2026, Fall 2025, etc."},
        },
        "required": ["student_id", "record_type"],
    },
    "output": {
        "type": "object",
        "properties": {
            "data": {
                "type": "object",
                "description": "Varies by record_type; see examples",
            },
            "last_updated": {"type": "string"},
        },
    },
}

# 6. Add Event to Calendar Tool
ADD_CALENDAR_EVENT_TOOL = {
    "name": "add_calendar_event",
    "description": "Add class, exam, or event to student's calendar (if linked).",
    "input_schema": {
        "type": "object",
        "properties": {
            "student_id": {"type": "string"},
            "event_title": {"type": "string"},
            "start_time": {"type": "string", "description": "ISO 8601"},
            "end_time": {"type": "string", "description": "ISO 8601"},
            "description": {"type": "string"},
            "location": {"type": "string"},
            "event_type": {
                "type": "string",
                "enum": ["class", "exam", "deadline", "event", "reminder"],
            },
        },
        "required": ["student_id", "event_title", "start_time", "end_time", "event_type"],
    },
    "output": {
        "type": "object",
        "properties": {
            "status": {"type": "string", "enum": ["added", "skipped_no_calendar_link", "failed"]},
            "calendar_event_id": {"type": "string"},
        },
    },
}

# Tool availability by role
TOOL_RBAC = {
    "student": ["recommend_courses", "schedule_meeting", "send_notification", "create_ticket", "get_student_record", "add_calendar_event"],
    "advisor": ["recommend_courses", "schedule_meeting", "send_notification", "create_ticket", "get_student_record"],
    "registrar": ["create_ticket", "send_notification"],
    "admin": ["recommend_courses", "schedule_meeting", "send_notification", "create_ticket", "get_student_record", "add_calendar_event"],
}

# Confirmations required before tool execution
TOOL_CONFIRMATIONS = {
    "send_notification": True,  # Always confirm before sending
    "add_calendar_event": True,
    "create_ticket": True,
    "schedule_meeting": True,
    "get_student_record": False,
    "recommend_courses": False,
}
