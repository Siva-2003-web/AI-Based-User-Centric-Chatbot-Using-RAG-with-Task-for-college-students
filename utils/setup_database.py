"""
Create and populate SQLite database for college management system.
Generates 20-50 mock records per table with realistic data.
"""

import sqlite3
from datetime import datetime, timedelta
import random
import csv
from pathlib import Path


def create_database(db_path: str = "data/database/college.db") -> sqlite3.Connection:
    """Create SQLite database and define schema."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Students table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            student_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            department TEXT NOT NULL,
            year INTEGER NOT NULL,
            roll_number TEXT,
            phone TEXT,
            password_hash TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Courses table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS courses (
            course_id TEXT PRIMARY KEY,
            course_name TEXT NOT NULL,
            department TEXT NOT NULL,
            credits INTEGER NOT NULL,
            semester TEXT NOT NULL,
            faculty_id TEXT NOT NULL,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (faculty_id) REFERENCES faculty(faculty_id)
        )
    """)

    # Faculty table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS faculty (
            faculty_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            department TEXT NOT NULL,
            email TEXT NOT NULL,
            office_location TEXT,
            office_hours TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Enrollments table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS enrollments (
            enrollment_id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL,
            course_id TEXT NOT NULL,
            semester TEXT NOT NULL,
            academic_year TEXT NOT NULL,
            grade TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES students(student_id),
            FOREIGN KEY (course_id) REFERENCES courses(course_id)
        )
    """)

    # Attendance table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS attendance (
            attendance_id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL,
            course_id TEXT NOT NULL,
            total_classes INTEGER NOT NULL,
            attended INTEGER NOT NULL,
            percentage REAL NOT NULL,
            semester TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES students(student_id),
            FOREIGN KEY (course_id) REFERENCES courses(course_id)
        )
    """)

    # Fees table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS fees (
            fee_id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL,
            total_fees REAL NOT NULL,
            paid_amount REAL NOT NULL,
            due_amount REAL NOT NULL,
            due_date TEXT NOT NULL,
            status TEXT NOT NULL,
            semester TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES students(student_id)
        )
    """)

    # Exams table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS exams (
            exam_id INTEGER PRIMARY KEY AUTOINCREMENT,
            course_id TEXT NOT NULL,
            exam_date TEXT NOT NULL,
            exam_time TEXT NOT NULL,
            room_number TEXT NOT NULL,
            exam_type TEXT NOT NULL,
            semester TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (course_id) REFERENCES courses(course_id)
        )
    """)

    # Conversation History table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS conversation_history (
            conversation_id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL,
            user_query TEXT NOT NULL,
            assistant_reply TEXT NOT NULL,
            sources TEXT,
            actions TEXT,
            model TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES students(student_id)
        )
    """)

    # Feedback table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS feedback (
            feedback_id INTEGER PRIMARY KEY AUTOINCREMENT,
            conversation_id INTEGER NOT NULL,
            student_id TEXT NOT NULL,
            rating INTEGER NOT NULL,
            comment TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (conversation_id) REFERENCES conversation_history(conversation_id),
            FOREIGN KEY (student_id) REFERENCES students(student_id)
        )
    """)

    conn.commit()
    return conn


def populate_database(conn: sqlite3.Connection) -> None:
    """Populate database with mock data."""
    cursor = conn.cursor()

    # Define departments and years
    departments = ["Computer Science", "Mathematics", "Biology", "Chemistry", "Physics", "English", "History"]
    semesters = ["Fall 2025", "Spring 2026", "Summer 2026"]
    years = [1, 2, 3, 4]
    grades = ["A", "A-", "B+", "B", "B-", "C+", "C", "C-", "D", "F"]

    # Insert Faculty (10 records)
    faculty_data = [
        ("F001", "Dr. Alice Johnson", "Computer Science", "alice@college.edu", "Tech 305", "MWF 2-4 PM"),
        ("F002", "Prof. Bob Chen", "Computer Science", "bob@college.edu", "Tech 310", "TTh 1-3 PM"),
        ("F003", "Dr. Sarah Williams", "Computer Science", "sarah@college.edu", "Tech 315", "W 10-12 PM, F 3-5 PM"),
        ("F004", "Prof. Michael Smith", "Mathematics", "michael@college.edu", "Sci 201", "MWF 11-12 PM"),
        ("F005", "Dr. Jennifer Lee", "Mathematics", "jennifer@college.edu", "Sci 205", "By Appointment"),
        ("F006", "Prof. David Brown", "Biology", "david@college.edu", "Sci 310", "TTh 11-1 PM"),
        ("F007", "Dr. Patricia Garcia", "Chemistry", "patricia@college.edu", "Sci 320", "MWF 1-2 PM"),
        ("F008", "Prof. Rebecca Martinez", "English", "rebecca@college.edu", "Hum 105", "TTh 2-4 PM"),
        ("F009", "Dr. James Wilson", "History", "james@college.edu", "Hum 210", "MWF 3-4:30 PM"),
        ("F010", "Prof. Lisa Anderson", "Psychology", "lisa@college.edu", "SS 150", "W 1-3 PM"),
    ]
    cursor.executemany(
        "INSERT OR IGNORE INTO faculty VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)",
        faculty_data,
    )
    print("✓ Inserted 10 faculty records")

    # Insert Courses (30 records)
    course_data = [
        ("CS101", "Introduction to Computer Science", "Computer Science", 3, "Fall 2025", "F001", "Fundamentals of programming"),
        ("CS201", "Data Structures", "Computer Science", 4, "Spring 2026", "F002", "Advanced data structures and algorithms"),
        ("CS301", "Artificial Intelligence", "Computer Science", 3, "Fall 2025", "F003", "AI techniques and applications"),
        ("MATH101", "Calculus I", "Mathematics", 4, "Fall 2025", "F004", "Single variable calculus"),
        ("MATH201", "Linear Algebra", "Mathematics", 3, "Spring 2026", "F005", "Matrix theory and applications"),
        ("BIO101", "General Biology", "Biology", 4, "Fall 2025", "F006", "Cell biology and genetics"),
        ("CHEM101", "General Chemistry", "Chemistry", 4, "Fall 2025", "F007", "Chemical bonding and reactions"),
        ("ENG101", "English Composition", "English", 3, "Fall 2025", "F008", "Academic writing skills"),
        ("HIST101", "World History", "History", 3, "Spring 2026", "F009", "Survey of major civilizations"),
        ("PSY101", "Intro to Psychology", "Psychology", 3, "Fall 2025", "F010", "Foundations of psychology"),
        ("CS102", "Programming 101", "Computer Science", 3, "Spring 2026", "F001", "Introduction to coding"),
        ("CS202", "Web Development", "Computer Science", 3, "Spring 2026", "F002", "Frontend and backend development"),
        ("MATH102", "Calculus II", "Mathematics", 4, "Spring 2026", "F004", "Integration and series"),
        ("BIO102", "Human Anatomy", "Biology", 4, "Spring 2026", "F006", "Human body systems"),
        ("CHEM102", "Organic Chemistry", "Chemistry", 4, "Spring 2026", "F007", "Organic reaction mechanisms"),
        ("ENG102", "Literature Analysis", "English", 3, "Spring 2026", "F008", "Critical reading and analysis"),
        ("HIST102", "American History", "History", 3, "Fall 2025", "F009", "US history from colonial to modern"),
        ("PSY102", "Developmental Psychology", "Psychology", 3, "Spring 2026", "F010", "Human development across lifespan"),
        ("CS303", "Machine Learning", "Computer Science", 3, "Fall 2025", "F003", "ML algorithms and applications"),
        ("MATH203", "Discrete Mathematics", "Mathematics", 3, "Fall 2025", "F005", "Logic, sets, combinatorics"),
        ("BIO203", "Ecology", "Biology", 3, "Fall 2025", "F006", "Population and community ecology"),
        ("CHEM203", "Biochemistry", "Chemistry", 3, "Spring 2026", "F007", "Biochemical processes"),
        ("ENG203", "World Literature", "English", 3, "Fall 2025", "F008", "Non-Western literature"),
        ("HIST203", "Medieval Europe", "History", 3, "Spring 2026", "F009", "Medieval political and social systems"),
        ("PSY203", "Social Psychology", "Psychology", 3, "Fall 2025", "F010", "Human social behavior"),
        ("CS401", "Capstone Project", "Computer Science", 3, "Spring 2026", "F001", "Senior CS project"),
        ("MATH401", "Real Analysis", "Mathematics", 3, "Fall 2025", "F004", "Rigorous analysis of real numbers"),
        ("BIO401", "Molecular Biology", "Biology", 4, "Spring 2026", "F006", "Molecular mechanisms of life"),
        ("CHEM401", "Physical Chemistry", "Chemistry", 4, "Fall 2025", "F007", "Thermodynamics and kinetics"),
        ("ENG401", "Senior Seminar", "English", 3, "Fall 2025", "F008", "Advanced literary analysis"),
    ]
    cursor.executemany(
        "INSERT OR IGNORE INTO courses VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)",
        course_data,
    )
    print("✓ Inserted 30 course records")

    # Insert Students (30 records) with default password "password123"
    from utils.auth import hash_password
    default_password_hash = hash_password("password123")
    
    student_data = []
    for i in range(1, 31):
        dept = random.choice(departments)
        year = random.choice(years)
        student_id = f"STU{i:05d}"
        name = f"Student {i}"
        email = f"student{i}@college.edu"
        roll_number = f"2025{i:04d}"
        phone = f"555-{1000 + i:04d}"
        student_data.append((student_id, name, email, dept, year, roll_number, phone, default_password_hash))
    
    cursor.executemany(
        "INSERT OR IGNORE INTO students (student_id, name, email, department, year, roll_number, phone, password_hash) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        student_data,
    )
    print("✓ Inserted 30 student records (password: password123)")

    # Get all student and course IDs
    cursor.execute("SELECT student_id FROM students")
    student_ids = [row[0] for row in cursor.fetchall()]
    
    cursor.execute("SELECT course_id FROM courses")
    course_ids = [row[0] for row in cursor.fetchall()]

    # Insert Enrollments (60-80 records)
    enrollment_data = []
    for student_id in student_ids:
        # Each student enrolled in 2-3 courses
        num_courses = random.randint(2, 3)
        for course_id in random.sample(course_ids, num_courses):
            semester = random.choice(semesters)
            academic_year = "2025-2026"
            grade = random.choice(grades)
            enrollment_data.append((student_id, course_id, semester, academic_year, grade))
    
    cursor.executemany(
        "INSERT INTO enrollments (student_id, course_id, semester, academic_year, grade, created_at) VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)",
        enrollment_data,
    )
    print(f"✓ Inserted {len(enrollment_data)} enrollment records")

    # Insert Attendance (match enrollments)
    attendance_data = []
    for enrollment in enrollment_data:
        student_id, course_id, semester, _, _ = enrollment
        total_classes = random.randint(30, 45)
        attended = random.randint(int(total_classes * 0.6), total_classes)
        percentage = (attended / total_classes) * 100
        attendance_data.append((student_id, course_id, total_classes, attended, percentage, semester))
    
    cursor.executemany(
        "INSERT INTO attendance (student_id, course_id, total_classes, attended, percentage, semester, created_at) VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)",
        attendance_data,
    )
    print(f"✓ Inserted {len(attendance_data)} attendance records")

    # Insert Fees (30 records, one per student)
    fees_data = []
    for student_id in student_ids:
        total_fees = random.choice([15000, 15000, 16000, 14500])  # Realistic tuition
        paid_amount = random.randint(int(total_fees * 0.5), int(total_fees * 0.95))
        due_amount = total_fees - paid_amount
        due_date = (datetime.now() + timedelta(days=random.randint(7, 90))).strftime("%Y-%m-%d")
        status = "Paid" if due_amount == 0 else "Pending" if due_amount < total_fees * 0.25 else "Due"
        semester = random.choice(semesters)
        fees_data.append((student_id, total_fees, paid_amount, due_amount, due_date, status, semester))
    
    cursor.executemany(
        "INSERT INTO fees (student_id, total_fees, paid_amount, due_amount, due_date, status, semester, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)",
        fees_data,
    )
    print(f"✓ Inserted {len(fees_data)} fee records")

    # Insert Exams (30 records, one per course)
    exam_data = []
    exam_types = ["Midterm", "Final", "Quiz"]
    rooms = [f"Room {i}" for i in range(101, 121)]
    
    cursor.execute("SELECT course_id, semester FROM courses")
    courses = cursor.fetchall()
    
    for course_id, semester in courses:
        exam_date = (datetime.now() + timedelta(days=random.randint(10, 60))).strftime("%Y-%m-%d")
        exam_time = random.choice(["9:00 AM", "10:00 AM", "1:00 PM", "2:00 PM", "3:00 PM"])
        room_number = random.choice(rooms)
        exam_type = random.choice(exam_types)
        exam_data.append((course_id, exam_date, exam_time, room_number, exam_type, semester))
    
    cursor.executemany(
        "INSERT INTO exams (course_id, exam_date, exam_time, room_number, exam_type, semester, created_at) VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)",
        exam_data,
    )
    print(f"✓ Inserted {len(exam_data)} exam records")

    conn.commit()


def export_to_csv(conn: sqlite3.Connection, output_dir: str = "data/database") -> None:
    """Export all tables to CSV files."""
    cursor = conn.cursor()
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    # Get all table names
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]

    for table_name in tables:
        cursor.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()
        
        # Get column names
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = [col[1] for col in cursor.fetchall()]

        # Write to CSV
        csv_path = f"{output_dir}/{table_name}.csv"
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(columns)
            writer.writerows(rows)
        
        print(f"  ✓ Exported {table_name} ({len(rows)} rows) to {csv_path}")


def run_setup() -> None:
    """Main database setup."""
    db_path = "data/database/college.db"
    print("=" * 60)
    print("College Database Setup")
    print("=" * 60)

    # Remove old database to ensure clean schema
    import os
    if os.path.exists(db_path):
        print(f"\nRemoving old database: {db_path}")
        os.remove(db_path)

    # Create database
    print("\nCreating database schema...")
    conn = create_database(db_path)

    # Populate with mock data
    print("\nPopulating with mock data...")
    populate_database(conn)

    # Export to CSV
    print("\nExporting tables to CSV...")
    export_to_csv(conn, "data/database")

    conn.close()

    print("\n" + "=" * 60)
    print(f"✓ Database created at: {db_path}")
    print("✓ CSV exports created in: data/database/")
    print("=" * 60)


if __name__ == "__main__":
    run_setup()
