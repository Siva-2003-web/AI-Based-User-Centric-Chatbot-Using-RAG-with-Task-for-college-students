"""Comprehensive test suite for Phase 6 Backend API.

Tests all endpoints with authentication, rate limiting, and file uploads:
- POST /api/auth/login
- GET /api/student/profile
- GET /api/student/attendance
- GET /api/student/schedule
- GET /api/student/fees
- POST /api/student/appointment
- POST /api/student/leave
- POST /api/upload
- GET /api/chat/history
- POST /api/chat/feedback
- POST /api/chat
- GET /api/analytics
"""

import requests
import io
import time
from pathlib import Path

BASE_URL = "http://localhost:8000"


def test_health_check():
    """Test basic health check."""
    print("\n" + "="*70)
    print("TEST: Health Check")
    print("="*70)
    
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✓ API is healthy: {data}")
    else:
        print(f"✗ Health check failed: {response.text}")


def test_login():
    """Test login endpoint and return token."""
    print("\n" + "="*70)
    print("TEST: POST /api/auth/login")
    print("="*70)
    
    # Test valid login
    print("\n1. Testing valid login...")
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"student_id": "STU00001", "password": "password123"}
    )
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        if data.get("success"):
            print(f"✓ Login successful!")
            print(f"  Token: {data['token'][:30]}...")
            print(f"  Name: {data['profile']['name']}")
            print(f"  Department: {data['profile']['department']}")
            token = data['token']
        else:
            print(f"✗ Login failed: {data.get('message')}")
            return None
    else:
        print(f"✗ Request failed: {response.text}")
        return None
    
    # Test invalid login
    print("\n2. Testing invalid login (wrong password)...")
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"student_id": "STU00001", "password": "wrongpassword"}
    )
    
    if response.status_code == 200:
        data = response.json()
        if not data.get("success"):
            print(f"✓ Correctly rejected invalid credentials")
        else:
            print(f"✗ Security issue: accepted wrong password")
    
    return token


def test_student_profile(token: str):
    """Test student profile endpoint."""
    print("\n" + "="*70)
    print("TEST: GET /api/student/profile")
    print("="*70)
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/api/student/profile", headers=headers)
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Profile retrieved successfully")
        print(f"  Name: {data['name']}")
        print(f"  Department: {data['department']}")
        print(f"  Year: {data['year']}")
        print(f"  Enrolled Courses: {len(data['enrolled_courses'])}")
        print(f"  Attendance Records: {len(data['attendance_summary'])}")
    else:
        print(f"✗ Failed: {response.text}")


def test_student_attendance(token: str):
    """Test attendance endpoint."""
    print("\n" + "="*70)
    print("TEST: GET /api/student/attendance")
    print("="*70)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Get all attendance
    print("\n1. Getting all attendance records...")
    response = requests.get(f"{BASE_URL}/api/student/attendance", headers=headers)
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Retrieved {data['count']} attendance records")
        for record in data['attendance'][:3]:
            alert = "🚨" if record['alert'] else "✓"
            print(f"  {alert} {record['course_name']}: {record['percentage']:.1f}% ({record['attended']}/{record['total_classes']})")
    else:
        print(f"✗ Failed: {response.text}")
    
    # Get specific course attendance
    print("\n2. Getting attendance for specific course (CS101)...")
    response = requests.get(
        f"{BASE_URL}/api/student/attendance",
        headers=headers,
        params={"course_id": "CS101"}
    )
    
    if response.status_code == 200:
        data = response.json()
        if data.get('found'):
            print(f"✓ CS101 Attendance: {data['percentage']:.1f}%")
        else:
            print(f"✗ No attendance found for CS101")


def test_student_schedule(token: str):
    """Test schedule endpoint."""
    print("\n" + "="*70)
    print("TEST: GET /api/student/schedule")
    print("="*70)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Get today's schedule
    print("\n1. Getting today's schedule...")
    response = requests.get(f"{BASE_URL}/api/student/schedule", headers=headers)
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Found {data['count']} classes for {data['date']}")
        for cls in data['classes'][:3]:
            print(f"  - {cls['course_name']}: {cls['meeting_times']}")
    else:
        print(f"✗ Failed: {response.text}")
    
    # Get schedule for specific date
    print("\n2. Getting schedule for 2026-01-10...")
    response = requests.get(
        f"{BASE_URL}/api/student/schedule",
        headers=headers,
        params={"date": "2026-01-10"}
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Found {data['count']} classes for 2026-01-10")


def test_student_fees(token: str):
    """Test fees endpoint."""
    print("\n" + "="*70)
    print("TEST: GET /api/student/fees")
    print("="*70)
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/api/student/fees", headers=headers)
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Fee status retrieved")
        print(f"  Semester: {data['semester']}")
        print(f"  Total: ${data['total']:.2f}")
        print(f"  Paid: ${data['paid']:.2f}")
        print(f"  Due: ${data['due']:.2f}")
        print(f"  Status: {data['status']}")
        print(f"  Due Date: {data['due_date']}")
    else:
        print(f"✗ Failed: {response.text}")


def test_book_appointment(token: str):
    """Test appointment booking endpoint."""
    print("\n" + "="*70)
    print("TEST: POST /api/student/appointment")
    print("="*70)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    appointment_data = {
        "faculty_id": "F001",
        "date": "2026-01-15",
        "time_slot": "14:00-14:30"
    }
    
    response = requests.post(
        f"{BASE_URL}/api/student/appointment",
        headers=headers,
        json=appointment_data
    )
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        if data.get('ok'):
            print(f"✓ Appointment booked successfully")
            print(f"  Appointment ID: {data['appointment_id']}")
            print(f"  Faculty: {data['faculty_id']}")
            print(f"  Date: {data['date']}")
            print(f"  Time: {data['time_slot']}")
        else:
            print(f"✗ Booking failed: {data.get('message')}")
    else:
        print(f"✗ Request failed: {response.text}")


def test_apply_leave(token: str):
    """Test leave application endpoint."""
    print("\n" + "="*70)
    print("TEST: POST /api/student/leave")
    print("="*70)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    leave_data = {
        "from_date": "2026-01-20",
        "to_date": "2026-01-22",
        "reason": "Medical appointment"
    }
    
    response = requests.post(
        f"{BASE_URL}/api/student/leave",
        headers=headers,
        json=leave_data
    )
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        if data.get('ok'):
            print(f"✓ Leave application submitted")
            print(f"  Ticket ID: {data['ticket_id']}")
            print(f"  From: {data['from_date']}")
            print(f"  To: {data['to_date']}")
            print(f"  Status: {data['status']}")
        else:
            print(f"✗ Application failed: {data.get('message')}")
    else:
        print(f"✗ Request failed: {response.text}")


def test_file_upload(token: str):
    """Test file upload endpoint."""
    print("\n" + "="*70)
    print("TEST: POST /api/upload")
    print("="*70)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create a fake PDF file
    print("\n1. Uploading a test PDF file...")
    fake_pdf_content = b"%PDF-1.4\n%Test document\n%%EOF"
    files = {"file": ("medical_certificate.pdf", io.BytesIO(fake_pdf_content), "application/pdf")}
    
    response = requests.post(
        f"{BASE_URL}/api/upload",
        headers=headers,
        files=files
    )
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            print(f"✓ File uploaded successfully")
            print(f"  Filename: {data['filename']}")
            print(f"  Size: {data['size']} bytes")
            print(f"  Path: {data['filepath']}")
        else:
            print(f"✗ Upload failed: {data.get('message')}")
    else:
        print(f"✗ Request failed: {response.text}")
    
    # Test invalid file type
    print("\n2. Testing invalid file type (.exe)...")
    fake_exe = b"MZ\x90\x00"
    files = {"file": ("virus.exe", io.BytesIO(fake_exe), "application/octet-stream")}
    
    response = requests.post(
        f"{BASE_URL}/api/upload",
        headers=headers,
        files=files
    )
    
    if response.status_code == 400:
        print(f"✓ Correctly rejected invalid file type")
    else:
        print(f"✗ Security issue: accepted invalid file type")


def test_chat_endpoint(token: str):
    """Test chat endpoint."""
    print("\n" + "="*70)
    print("TEST: POST /api/chat")
    print("="*70)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    chat_data = {
        "messages": [
            {"role": "user", "content": "What's my attendance in CS101?"}
        ],
        "tools_enabled": True
    }
    
    response = requests.post(
        f"{BASE_URL}/api/chat",
        headers=headers,
        json=chat_data
    )
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Chat response received")
        print(f"  Reply: {data['reply'][:150]}...")
        print(f"  Sources: {len(data.get('sources', []))}")
        print(f"  Actions: {len(data.get('actions', []))}")
        if data.get('actions'):
            print(f"  Action: {data['actions'][0][:100]}...")
    else:
        print(f"✗ Failed: {response.text}")


def test_chat_history(token: str):
    """Test chat history endpoint."""
    print("\n" + "="*70)
    print("TEST: GET /api/chat/history")
    print("="*70)
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(
        f"{BASE_URL}/api/chat/history",
        headers=headers,
        params={"limit": 5}
    )
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Retrieved {data['count']} conversations")
        for conv in data['conversations'][:2]:
            print(f"\n  [{conv['conversation_id']}] {conv['created_at']}")
            print(f"  Q: {conv['user_query'][:70]}...")
            print(f"  A: {conv['assistant_reply'][:70]}...")
    else:
        print(f"✗ Failed: {response.text}")


def test_analytics(token: str):
    """Test analytics endpoint."""
    print("\n" + "="*70)
    print("TEST: GET /api/analytics")
    print("="*70)
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/api/analytics", headers=headers)
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Analytics retrieved")
        
        stats = data.get('global_stats', {})
        print(f"\n  Global Stats:")
        print(f"    Total Conversations: {stats.get('total_conversations', 0)}")
        print(f"    Unique Students: {stats.get('unique_students', 0)}")
        
        if 'student_stats' in data:
            st_stats = data['student_stats']
            print(f"\n  Your Stats:")
            print(f"    Your Conversations: {st_stats.get('total_conversations', 0)}")
        
        print(f"\n  Most Asked Questions: {len(data.get('most_asked_questions', []))}")
    else:
        print(f"✗ Failed: {response.text}")


def test_rate_limiting():
    """Test rate limiting by making rapid requests."""
    print("\n" + "="*70)
    print("TEST: Rate Limiting")
    print("="*70)
    
    print("\nMaking 65 rapid requests to /health (limit: 60/minute)...")
    
    success_count = 0
    rate_limited_count = 0
    
    for i in range(65):
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            success_count += 1
        elif response.status_code == 429:
            rate_limited_count += 1
    
    print(f"  Successful requests: {success_count}")
    print(f"  Rate limited requests: {rate_limited_count}")
    
    if rate_limited_count > 0:
        print(f"✓ Rate limiting is working correctly")
    else:
        print(f"⚠ Rate limiting may not be working (no 429 responses)")


def test_unauthenticated_access():
    """Test that protected endpoints reject unauthenticated requests."""
    print("\n" + "="*70)
    print("TEST: Unauthenticated Access Protection")
    print("="*70)
    
    protected_endpoints = [
        ("GET", "/api/student/profile"),
        ("GET", "/api/student/attendance"),
        ("GET", "/api/student/schedule"),
        ("GET", "/api/student/fees"),
        ("POST", "/api/student/appointment"),
        ("POST", "/api/student/leave"),
        ("POST", "/api/upload"),
        ("GET", "/api/chat/history"),
    ]
    
    for method, endpoint in protected_endpoints:
        if method == "GET":
            response = requests.get(f"{BASE_URL}{endpoint}")
        else:
            response = requests.post(f"{BASE_URL}{endpoint}", json={})
        
        if response.status_code == 401:
            print(f"✓ {method} {endpoint}: Correctly requires auth")
        else:
            print(f"✗ {method} {endpoint}: Missing auth check (got {response.status_code})")


def run_all_tests():
    """Run all Phase 6 API tests."""
    print("\n" + "="*70)
    print("PHASE 6 BACKEND API TEST SUITE")
    print("="*70)
    print("\nEnsure API is running: uvicorn api.main:app --reload")
    print("Ensure database is updated: python -m utils.setup_database")
    
    try:
        # Health check
        test_health_check()
        
        # Login and get token
        token = test_login()
        if not token:
            print("\n✗ Cannot proceed without authentication token")
            return
        
        # Test all endpoints
        test_student_profile(token)
        test_student_attendance(token)
        test_student_schedule(token)
        test_student_fees(token)
        test_book_appointment(token)
        test_apply_leave(token)
        test_file_upload(token)
        test_chat_endpoint(token)
        test_chat_history(token)
        test_analytics(token)
        
        # Security tests
        test_unauthenticated_access()
        test_rate_limiting()
        
        print("\n" + "="*70)
        print("✅ ALL PHASE 6 TESTS COMPLETED!")
        print("="*70)
        
    except requests.exceptions.ConnectionError:
        print("\n✗ Cannot connect to API. Start with: uvicorn api.main:app --reload")
    except Exception as e:
        print(f"\n✗ Test error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_all_tests()
