"""
Quick Integration Test - Rapid validation of key scenarios

Run this for a fast check of system functionality.
"""

import requests
import json

BASE_URL = "http://127.0.0.1:8000/api"
STUDENT_ID = "STU00001"
PASSWORD = "password123"


def test():
    """Quick test of main functionality."""
    print("=" * 60)
    print("QUICK INTEGRATION TEST")
    print("=" * 60)
    
    # 1. Login
    print("\n1️⃣  Testing Login...")
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json={"student_id": STUDENT_ID, "password": PASSWORD}
    )
    
    if response.status_code == 200:
        data = response.json()
        token = data["token"]
        print(f"✅ Login successful! Token: {token[:20]}...")
    else:
        print(f"❌ Login failed: {response.status_code}")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # 2. Get Profile
    print("\n2️⃣  Testing Profile...")
    response = requests.get(f"{BASE_URL}/student/profile", headers=headers)
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Profile: {data.get('name')} - {data.get('department')}")
    else:
        print(f"❌ Profile failed: {response.status_code}")
    
    # 3. Get Attendance
    print("\n3️⃣  Testing Attendance...")
    response = requests.get(f"{BASE_URL}/student/attendance", headers=headers)
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Attendance: {data.get('count')} courses")
        for att in data.get('attendance', [])[:2]:
            print(f"   - {att['course_name']}: {att['percentage']}%")
    else:
        print(f"❌ Attendance failed: {response.status_code}")
    
    # 4. Get Schedule
    print("\n4️⃣  Testing Schedule...")
    response = requests.get(f"{BASE_URL}/student/schedule", headers=headers)
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Schedule: {data.get('count')} classes today")
    else:
        print(f"❌ Schedule failed: {response.status_code}")
    
    # 5. Chat Query
    print("\n5️⃣  Testing Chat...")
    response = requests.post(
        f"{BASE_URL}/chat",
        headers=headers,
        json={"messages": [{"role": "user", "content": "What's my attendance?"}]}
    )
    if response.status_code == 200:
        data = response.json()
        reply = data.get('reply', '')
        print(f"✅ Chat response: {reply[:100]}...")
    else:
        print(f"❌ Chat failed: {response.status_code}")
    
    # 6. Book Appointment
    print("\n6️⃣  Testing Appointment Booking...")
    response = requests.post(
        f"{BASE_URL}/student/book-appointment",
        headers=headers,
        json={
            "faculty_id": "FAC001",
            "date": "2026-01-10",
            "time_slot": "10:00-11:00",
            "purpose": "Test appointment"
        }
    )
    if response.status_code == 200:
        print("✅ Appointment booked successfully")
    else:
        print(f"❌ Appointment failed: {response.status_code}")
    
    print("\n" + "=" * 60)
    print("QUICK TEST COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    try:
        test()
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        print("Make sure backend is running: uvicorn api.main:app --reload")
