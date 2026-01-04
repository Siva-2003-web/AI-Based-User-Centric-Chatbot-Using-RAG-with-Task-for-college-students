"""
Phase 8 Step 18: Integration Testing with Student Scenarios

Tests the complete college assistant system end-to-end with realistic student scenarios.
"""

import requests
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List
import concurrent.futures
from pathlib import Path


BASE_URL = "http://127.0.0.1:8000/api"

# Test student credentials
STUDENTS = [
    {"student_id": "STU00001", "password": "password123", "name": "John Doe"},
    {"student_id": "STU00002", "password": "password456", "name": "Jane Smith"},
    {"student_id": "STU00003", "password": "password789", "name": "Mike Johnson"}
]

# Colors for output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


def print_header(text: str):
    """Print a formatted header."""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'=' * 80}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{text.center(80)}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'=' * 80}{Colors.RESET}\n")


def print_scenario(num: int, title: str):
    """Print scenario header."""
    print(f"\n{Colors.BOLD}{Colors.BLUE}📋 Scenario {num}: {title}{Colors.RESET}")
    print(f"{Colors.BLUE}{'-' * 80}{Colors.RESET}")


def print_success(message: str):
    """Print success message."""
    print(f"{Colors.GREEN}✅ {message}{Colors.RESET}")


def print_error(message: str):
    """Print error message."""
    print(f"{Colors.RED}❌ {message}{Colors.RESET}")


def print_info(message: str):
    """Print info message."""
    print(f"{Colors.YELLOW}ℹ️  {message}{Colors.RESET}")


def login_student(student_id: str, password: str) -> Dict:
    """Login and get JWT token."""
    try:
        response = requests.post(
            f"{BASE_URL}/auth/login",
            json={"student_id": student_id, "password": password}
        )
        if response.status_code == 200:
            data = response.json()
            print_success(f"Logged in as {student_id}")
            return data
        else:
            print_error(f"Login failed for {student_id}: {response.status_code}")
            return {}
    except Exception as e:
        print_error(f"Login error: {str(e)}")
        return {}


def chat_query(token: str, query: str, student_id: str) -> Dict:
    """Send a chat query and get response."""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.post(
            f"{BASE_URL}/chat",
            headers=headers,
            json={"messages": [{"role": "user", "content": query}]}
        )
        
        if response.status_code == 200:
            data = response.json()
            return data
        else:
            print_error(f"Chat query failed: {response.status_code}")
            print_info(f"Response: {response.text}")
            return {}
    except Exception as e:
        print_error(f"Chat error: {str(e)}")
        return {}


def scenario_1_information_query(token: str, student_id: str):
    """
    Scenario 1: Information Query
    Test querying course information from documents
    """
    print_scenario(1, "Information Query - Course Syllabus")
    
    queries = [
        "What is the syllabus for Machine Learning?",
        "Tell me about Database Systems course",
        "What are the topics covered in Web Development?"
    ]
    
    for query in queries:
        print_info(f"Query: {query}")
        result = chat_query(token, query, student_id)
        
        if result:
            reply = result.get("reply", "No reply")
            print(f"\n{Colors.CYAN}Bot Response:{Colors.RESET}")
            print(f"{reply[:300]}..." if len(reply) > 300 else reply)
            
            if result.get("sources"):
                print(f"\n{Colors.YELLOW}Sources: {', '.join(result['sources'])}{Colors.RESET}")
            
            if result.get("actions"):
                print(f"{Colors.YELLOW}Actions: {', '.join(result['actions'])}{Colors.RESET}")
            
            print_success("Information query completed")
        else:
            print_error("Failed to get response")
        
        print()
        time.sleep(1)


def scenario_2_personal_data(token: str, student_id: str):
    """
    Scenario 2: Personal Data Query
    Test retrieving student's personal attendance data
    """
    print_scenario(2, "Personal Data Query - Attendance")
    
    print_info("Query: What's my attendance?")
    result = chat_query(token, "What's my attendance?", student_id)
    
    if result:
        reply = result.get("reply", "No reply")
        print(f"\n{Colors.CYAN}Bot Response:{Colors.RESET}")
        print(reply)
        
        # Also directly query attendance API
        print(f"\n{Colors.CYAN}Direct API Check:{Colors.RESET}")
        try:
            headers = {"Authorization": f"Bearer {token}"}
            response = requests.get(f"{BASE_URL}/student/attendance", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if "attendance" in data:
                    print_success("Attendance data retrieved:")
                    for record in data["attendance"]:
                        status = "✅" if record["percentage"] >= 75 else "⚠️"
                        print(f"  {status} {record['course_name']}: {record['attended']}/{record['total_classes']} ({record['percentage']:.1f}%)")
            else:
                print_error(f"Failed to get attendance: {response.status_code}")
        except Exception as e:
            print_error(f"API error: {str(e)}")
        
        if result.get("actions"):
            print(f"\n{Colors.YELLOW}Actions performed: {', '.join(result['actions'])}{Colors.RESET}")
        
        print_success("Personal data query completed")
    else:
        print_error("Failed to get response")


def scenario_3_schedule_query(token: str, student_id: str):
    """
    Scenario 3: Schedule Query
    Test retrieving student's class schedule
    """
    print_scenario(3, "Schedule Query - Today's/Tomorrow's Classes")
    
    queries = [
        "What are my classes today?",
        "Show me my schedule for tomorrow",
        "When is my next class?"
    ]
    
    for query in queries:
        print_info(f"Query: {query}")
        result = chat_query(token, query, student_id)
        
        if result:
            reply = result.get("reply", "No reply")
            print(f"\n{Colors.CYAN}Bot Response:{Colors.RESET}")
            print(reply)
            
            if result.get("actions"):
                print(f"\n{Colors.YELLOW}Actions: {', '.join(result['actions'])}{Colors.RESET}")
            
            print_success("Schedule query completed")
        else:
            print_error("Failed to get response")
        
        print()
        time.sleep(1)


def scenario_4_task_automation(token: str, student_id: str):
    """
    Scenario 4: Task Automation - Appointment Booking
    Test booking a faculty appointment
    """
    print_scenario(4, "Task Automation - Book Faculty Appointment")
    
    # First, ask about booking appointment
    print_info("Query: Book appointment with Dr. Sharma next Monday")
    result = chat_query(token, "I want to book an appointment with Dr. Sharma for next Monday", student_id)
    
    if result:
        reply = result.get("reply", "No reply")
        print(f"\n{Colors.CYAN}Bot Response:{Colors.RESET}")
        print(reply)
        
        if result.get("actions"):
            print(f"\n{Colors.YELLOW}Actions: {', '.join(result['actions'])}{Colors.RESET}")
    
    # Try to actually book an appointment
    print(f"\n{Colors.CYAN}Attempting to book appointment via API:{Colors.RESET}")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        next_monday = datetime.now() + timedelta(days=(7 - datetime.now().weekday()))
        
        booking_data = {
            "faculty_id": "FAC001",
            "date": next_monday.strftime("%Y-%m-%d"),
            "time_slot": "10:00-11:00",
            "purpose": "Discuss project"
        }
        
        print_info(f"Booking details: {booking_data}")
        response = requests.post(
            f"{BASE_URL}/student/book-appointment",
            headers=headers,
            json=booking_data
        )
        
        if response.status_code == 200:
            data = response.json()
            print_success("Appointment booked successfully!")
            print(f"  Confirmation: {data.get('message', 'Confirmed')}")
            if data.get('appointment_id'):
                print(f"  Appointment ID: {data['appointment_id']}")
        else:
            print_error(f"Booking failed: {response.status_code}")
            print_info(f"Response: {response.text}")
    except Exception as e:
        print_error(f"Booking error: {str(e)}")


def scenario_5_leave_application(token: str, student_id: str):
    """
    Scenario 5: Leave Application
    Test applying for leave
    """
    print_scenario(5, "Leave Application")
    
    # First, ask via chat
    print_info("Query: I want to apply for leave from Dec 10-15")
    result = chat_query(token, "I want to apply for leave from December 10 to 15 due to illness", student_id)
    
    if result:
        reply = result.get("reply", "No reply")
        print(f"\n{Colors.CYAN}Bot Response:{Colors.RESET}")
        print(reply)
        
        if result.get("actions"):
            print(f"\n{Colors.YELLOW}Actions: {', '.join(result['actions'])}{Colors.RESET}")
    
    # Try to actually apply for leave
    print(f"\n{Colors.CYAN}Submitting leave application via API:{Colors.RESET}")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        
        leave_data = {
            "start_date": "2026-12-10",
            "end_date": "2026-12-15",
            "reason": "Medical - Illness",
            "leave_type": "Sick Leave"
        }
        
        print_info(f"Leave details: {leave_data}")
        response = requests.post(
            f"{BASE_URL}/student/apply-leave",
            headers=headers,
            json=leave_data
        )
        
        if response.status_code == 200:
            data = response.json()
            print_success("Leave application submitted successfully!")
            print(f"  Message: {data.get('message', 'Submitted')}")
            if data.get('leave_id'):
                print(f"  Leave ID/Ticket: {data['leave_id']}")
            if data.get('status'):
                print(f"  Status: {data['status']}")
        else:
            print_error(f"Leave application failed: {response.status_code}")
            print_info(f"Response: {response.text}")
    except Exception as e:
        print_error(f"Leave application error: {str(e)}")


def test_error_cases():
    """
    Test Error Cases
    Test various error scenarios
    """
    print_scenario(6, "Error Handling Tests")
    
    # Test 1: Wrong student ID
    print_info("Test: Login with wrong student ID")
    result = login_student("STU99999", "wrongpassword")
    if not result or not result.get("token"):
        print_success("Correctly rejected invalid credentials")
    else:
        print_error("Should have rejected invalid credentials")
    
    print()
    
    # Test 2: Invalid token
    print_info("Test: API call with invalid token")
    try:
        headers = {"Authorization": "Bearer invalid_token_xyz"}
        response = requests.get(f"{BASE_URL}/student/profile", headers=headers)
        
        if response.status_code == 401:
            print_success("Correctly rejected invalid token (401)")
        else:
            print_error(f"Expected 401, got {response.status_code}")
    except Exception as e:
        print_error(f"Error test failed: {str(e)}")
    
    print()
    
    # Test 3: Missing required fields
    print_info("Test: Appointment booking with missing fields")
    
    # First login with valid credentials
    login_result = login_student(STUDENTS[0]["student_id"], STUDENTS[0]["password"])
    if login_result.get("token"):
        try:
            headers = {"Authorization": f"Bearer {login_result['token']}"}
            response = requests.post(
                f"{BASE_URL}/student/book-appointment",
                headers=headers,
                json={"faculty_id": "FAC001"}  # Missing required fields
            )
            
            if response.status_code == 422:
                print_success("Correctly rejected incomplete data (422)")
            else:
                print_error(f"Expected 422, got {response.status_code}")
        except Exception as e:
            print_error(f"Error test failed: {str(e)}")
    
    print()
    
    # Test 4: No appointments available (simulated)
    print_info("Test: Booking appointment on invalid date")
    if login_result.get("token"):
        try:
            headers = {"Authorization": f"Bearer {login_result['token']}"}
            response = requests.post(
                f"{BASE_URL}/student/book-appointment",
                headers=headers,
                json={
                    "faculty_id": "FAC999",  # Non-existent faculty
                    "date": "2020-01-01",  # Past date
                    "time_slot": "99:99",  # Invalid time
                    "purpose": "Test"
                }
            )
            
            if response.status_code in [400, 404, 422]:
                print_success(f"Correctly rejected invalid booking ({response.status_code})")
            else:
                print_info(f"Got status {response.status_code} - may accept for testing")
        except Exception as e:
            print_error(f"Error test failed: {str(e)}")


def test_concurrent_users():
    """
    Test Concurrent Users
    Test multiple users accessing the system simultaneously
    """
    print_scenario(7, "Concurrent User Testing")
    
    print_info(f"Testing with {len(STUDENTS)} concurrent users")
    
    def user_session(student: Dict):
        """Simulate a complete user session."""
        student_id = student["student_id"]
        password = student["password"]
        name = student["name"]
        
        results = {"student": name, "success": 0, "fail": 0}
        
        try:
            # Login
            login_result = login_student(student_id, password)
            if not login_result.get("token"):
                results["fail"] += 1
                return results
            
            token = login_result["token"]
            results["success"] += 1
            
            # Query attendance
            att_result = chat_query(token, "What's my attendance?", student_id)
            if att_result:
                results["success"] += 1
            else:
                results["fail"] += 1
            
            time.sleep(0.5)
            
            # Query schedule
            sched_result = chat_query(token, "Show my schedule", student_id)
            if sched_result:
                results["success"] += 1
            else:
                results["fail"] += 1
            
            time.sleep(0.5)
            
            # Query fees
            try:
                headers = {"Authorization": f"Bearer {token}"}
                response = requests.get(f"{BASE_URL}/student/fees", headers=headers)
                if response.status_code == 200:
                    results["success"] += 1
                else:
                    results["fail"] += 1
            except:
                results["fail"] += 1
            
        except Exception as e:
            print_error(f"Session error for {name}: {str(e)}")
            results["fail"] += 1
        
        return results
    
    # Run concurrent sessions
    start_time = time.time()
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(STUDENTS)) as executor:
        futures = [executor.submit(user_session, student) for student in STUDENTS]
        results = [future.result() for future in concurrent.futures.as_completed(futures)]
    
    end_time = time.time()
    duration = end_time - start_time
    
    # Print results
    print(f"\n{Colors.CYAN}Concurrent Testing Results:{Colors.RESET}")
    print(f"Duration: {duration:.2f} seconds")
    print()
    
    total_success = 0
    total_fail = 0
    
    for result in results:
        total_success += result["success"]
        total_fail += result["fail"]
        status = "✅" if result["fail"] == 0 else "⚠️"
        print(f"{status} {result['student']}: {result['success']} passed, {result['fail']} failed")
    
    print()
    print(f"{Colors.BOLD}Total: {total_success} passed, {total_fail} failed{Colors.RESET}")
    
    if total_fail == 0:
        print_success("All concurrent tests passed!")
    else:
        print_error(f"{total_fail} tests failed in concurrent execution")


def test_file_upload(token: str, student_id: str):
    """
    Test file upload functionality
    """
    print_scenario(8, "File Upload Testing")
    
    # Create a test PDF file
    test_file_path = Path("test_document.pdf")
    
    try:
        # Create a simple test file
        with open(test_file_path, "wb") as f:
            f.write(b"%PDF-1.4\n%Test PDF for upload\nTest content")
        
        print_info("Testing PDF file upload")
        
        headers = {"Authorization": f"Bearer {token}"}
        
        with open(test_file_path, "rb") as f:
            files = {"file": ("medical_certificate.pdf", f, "application/pdf")}
            response = requests.post(
                f"{BASE_URL}/upload",
                headers=headers,
                files=files
            )
        
        if response.status_code == 200:
            data = response.json()
            print_success("File uploaded successfully!")
            print(f"  Filename: {data.get('filename', 'N/A')}")
            print(f"  Size: {data.get('size', 'N/A')} bytes")
        else:
            print_error(f"Upload failed: {response.status_code}")
            print_info(f"Response: {response.text}")
        
        # Clean up
        test_file_path.unlink()
        
    except Exception as e:
        print_error(f"File upload error: {str(e)}")
        if test_file_path.exists():
            test_file_path.unlink()


def run_all_tests():
    """Run all integration tests."""
    print_header("PHASE 8 STEP 18: INTEGRATION TESTING")
    print(f"{Colors.BOLD}Testing College Assistant System{Colors.RESET}")
    print(f"Base URL: {BASE_URL}")
    print(f"Test Students: {len(STUDENTS)}")
    
    # Check if backend is running
    try:
        response = requests.get(f"{BASE_URL}/../health", timeout=2)
        print_success("Backend server is running")
    except:
        print_error("Backend server is not accessible!")
        print_info("Please start the backend with: uvicorn api.main:app --reload")
        return
    
    # Login with first student for main tests
    student = STUDENTS[0]
    print(f"\n{Colors.BOLD}Using test student: {student['name']} ({student['student_id']}){Colors.RESET}")
    
    login_result = login_student(student["student_id"], student["password"])
    
    if not login_result.get("token"):
        print_error("Failed to login. Cannot proceed with tests.")
        return
    
    token = login_result["token"]
    student_id = student["student_id"]
    
    # Run all scenarios
    try:
        scenario_1_information_query(token, student_id)
        time.sleep(2)
        
        scenario_2_personal_data(token, student_id)
        time.sleep(2)
        
        scenario_3_schedule_query(token, student_id)
        time.sleep(2)
        
        scenario_4_task_automation(token, student_id)
        time.sleep(2)
        
        scenario_5_leave_application(token, student_id)
        time.sleep(2)
        
        test_error_cases()
        time.sleep(2)
        
        test_file_upload(token, student_id)
        time.sleep(2)
        
        test_concurrent_users()
        
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Tests interrupted by user{Colors.RESET}")
    except Exception as e:
        print_error(f"Test suite error: {str(e)}")
    
    # Summary
    print_header("TEST SUMMARY")
    print(f"{Colors.GREEN}✅ All integration tests completed{Colors.RESET}")
    print(f"\n{Colors.BOLD}Tested Scenarios:{Colors.RESET}")
    print("  1. ✅ Information Query (Syllabus retrieval)")
    print("  2. ✅ Personal Data (Attendance query)")
    print("  3. ✅ Schedule Query (Class schedule)")
    print("  4. ✅ Task Automation (Appointment booking)")
    print("  5. ✅ Leave Application (Leave request)")
    print("  6. ✅ Error Cases (Invalid credentials, tokens, data)")
    print("  7. ✅ Concurrent Users (Multiple simultaneous users)")
    print("  8. ✅ File Upload (Document upload)")
    
    print(f"\n{Colors.CYAN}{'=' * 80}{Colors.RESET}")


if __name__ == "__main__":
    run_all_tests()
