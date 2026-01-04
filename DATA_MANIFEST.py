"""
Data collection manifest for College Assistant Chatbot.
Documents source locations, formats, update frequency, and processing notes.
"""

DATA_MANIFEST = {
    "catalogs": {
        "course_catalog_2025_2026.csv": {
            "description": "Complete course listings with prerequisites, credits, descriptions, instructors, meeting times",
            "format": "CSV",
            "update_frequency": "Annually (June)",
            "source": "Registrar's Office",
            "columns": ["course_code", "course_title", "department", "credits", "level", "prerequisites", "description", "instructor", "semester_offered", "capacity", "meeting_times"],
            "use_cases": ["course_recommendations", "course_search", "schedule_building", "prerequisite_checking"],
            "size_approx": "10-15 KB",
        }
    },
    "handbook": {
        "student_handbook_2025_2026.txt": {
            "description": "Student handbook with policies, procedures, support services, codes of conduct, FAQ",
            "format": "Markdown/Text",
            "update_frequency": "Annually (June) + ad-hoc for policy changes",
            "source": "Student Affairs Office",
            "sections": ["Academic Policies", "Student Life", "Support Services", "Financial Info", "Technology", "Library", "Facilities", "Safety", "Diversity", "FAQ"],
            "use_cases": ["policy_questions", "procedures", "faq", "support_resources", "appeal_processes"],
            "size_approx": "80-100 KB",
        }
    },
    "faculty": {
        "faculty_directory.csv": {
            "description": "Complete faculty directory with contact info, office hours, research interests",
            "format": "CSV",
            "update_frequency": "Bi-annually (June, January)",
            "source": "HR / Faculty Affairs",
            "columns": ["faculty_id", "name", "department", "email", "office_location", "office_hours", "phone", "research_interests", "degree", "years_at_college"],
            "use_cases": ["faculty_contact", "office_hours", "research_interests", "course_instructor_lookup"],
            "size_approx": "20-30 KB",
        },
        "department_info.txt": {
            "description": "Department-specific info (majors, core courses, research opportunities, career outcomes)",
            "format": "Markdown/Text",
            "update_frequency": "Annually (June)",
            "source": "Department Chairs",
            "sections": ["Department Overview", "Majors Offered", "Core Courses", "Specialization Tracks", "Research", "Career Outcomes", "Contact"],
            "use_cases": ["major_selection", "degree_requirements", "research_opportunities", "career_advising"],
            "size_approx": "40-60 KB",
        }
    },
    "calendar": {
        "academic_calendar_2025_2026.csv": {
            "description": "Academic calendar with key dates (semester start, breaks, exams, deadlines, graduation)",
            "format": "CSV",
            "update_frequency": "Annually (June)",
            "source": "Registrar's Office",
            "columns": ["event", "date_start", "date_end", "description"],
            "use_cases": ["deadline_reminders", "semester_planning", "event_scheduling", "exam_notifications"],
            "size_approx": "5-10 KB",
        }
    },
    "facilities": {
        "campus_facilities.csv": {
            "description": "Campus facilities directory with hours, contact, and services offered",
            "format": "CSV",
            "update_frequency": "Quarterly (at semester start)",
            "source": "Campus Operations / Facilities Management",
            "columns": ["facility_name", "location", "type", "hours_open", "hours_close", "contact_phone", "contact_email", "key_services"],
            "use_cases": ["facility_lookup", "hours_inquiry", "service_location", "campus_navigation"],
            "size_approx": "15-25 KB",
        }
    },
    "fees_scholarships": {
        "fees_scholarships_2025_2026.csv": {
            "description": "Tuition, fees breakdown, and scholarship/grant information with eligibility",
            "format": "CSV",
            "update_frequency": "Annually (April for next year)",
            "source": "Financial Aid / Business Office",
            "tables": ["Fees", "Scholarships"],
            "use_cases": ["cost_inquiry", "scholarship_eligibility", "financial_planning", "aid_questions"],
            "size_approx": "25-35 KB",
        }
    }
}

# Data ingestion processing notes
INGESTION_NOTES = {
    "csv_documents": [
        "course_catalog_2025_2026.csv",
        "faculty_directory.csv",
        "academic_calendar_2025_2026.csv",
        "campus_facilities.csv",
        "fees_scholarships_2025_2026.csv",
    ],
    "text_documents": [
        "student_handbook_2025_2026.txt",
        "department_info.txt",
    ],
    "processing_steps": [
        "1. Load CSV files with pandas; text files as raw strings",
        "2. Normalize text encoding (UTF-8)",
        "3. Create document chunks (500-token chunks with overlap)",
        "4. Extract metadata (source file, section, update date, document type)",
        "5. Generate embeddings (OpenAI text-embedding-3-small or local model)",
        "6. Upsert into vector DB (Chroma or Pinecone) with metadata filters",
        "7. Build sparse index (BM25) for hybrid search",
    ],
    "metadata_schema": {
        "source_file": "str",
        "document_type": "str (course, policy, faculty, facilities, financial, calendar)",
        "section": "str (handbook section, department, etc.)",
        "last_updated": "date",
        "confidentiality": "str (public, restricted, internal)",
        "chunk_index": "int",
    },
    "redaction_rules": [
        "Remove student IDs, SSNs, financial account numbers from all documents",
        "Redact personal email addresses (use department contact instead)",
        "Redact emergency contact numbers (use main line instead)",
        "Mask faculty home addresses (retain office location only)",
    ],
}

# Test data summary
TEST_DATA_STATS = {
    "total_documents": 8,
    "total_size_approx_kb": "200-350",
    "expected_chunks": "300-500 (depending on chunking strategy)",
    "data_ready_for_ingestion": True,
    "next_step": "Run utils.ingest with embedding + vector store wiring",
}
