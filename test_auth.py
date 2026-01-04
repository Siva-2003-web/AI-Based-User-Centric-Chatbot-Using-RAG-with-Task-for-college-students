"""Test script for authentication flow and personalized queries.

Tests:
1. Login with valid credentials
2. Login with invalid credentials
3. Fetch profile with valid token
4. Chat with authenticated context (personalized queries)
"""

import requests
import json

BASE_URL = "http://localhost:8000"


def test_login():
    """Test student login endpoint."""
    print("\n" + "=" * 70)
    print("TEST 1: Login with valid credentials")
    print("=" * 70)
    
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"student_id": "STU00001", "password": "password123"}
    )
    
    print(f"Status: {response.status_code}")
    data = response.json()
    print(json.dumps(data, indent=2))
    
    if data.get("success"):
        token = data.get("token")
        print(f"\n✓ Login successful! Token: {token[:50]}...")
        return token
    else:
        print(f"\n✗ Login failed: {data.get('message')}")
        return None


def test_invalid_login():
    """Test login with wrong password."""
    print("\n" + "=" * 70)
    print("TEST 2: Login with invalid credentials")
    print("=" * 70)
    
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"student_id": "STU00001", "password": "wrongpassword"}
    )
    
    print(f"Status: {response.status_code}")
    data = response.json()
    print(json.dumps(data, indent=2))
    
    if not data.get("success"):
        print("\n✓ Invalid login correctly rejected")
    else:
        print("\n✗ Security issue: invalid login accepted!")


def test_profile(token: str):
    """Test fetching profile with authentication."""
    print("\n" + "=" * 70)
    print("TEST 3: Fetch profile with authentication")
    print("=" * 70)
    
    response = requests.get(
        f"{BASE_URL}/api/student/profile",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    print(f"Status: {response.status_code}")
    data = response.json()
    print(json.dumps(data, indent=2, default=str))
    
    if response.status_code == 200:
        print("\n✓ Profile fetched successfully")
    else:
        print(f"\n✗ Profile fetch failed")


def test_personalized_chat(token: str):
    """Test chat with authenticated context."""
    print("\n" + "=" * 70)
    print("TEST 4: Personalized chat queries")
    print("=" * 70)
    
    queries = [
        "What's my schedule today?",
        "Check my attendance",
        "Show my grades",
    ]
    
    for query in queries:
        print(f"\nQuery: {query}")
        response = requests.post(
            f"{BASE_URL}/api/chat",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "messages": [{"role": "user", "content": query}],
                "tools_enabled": True
            }
        )
        
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Reply: {data.get('reply', 'N/A')[:200]}...")
            if data.get("actions"):
                print(f"Actions: {data['actions']}")
        else:
            print(f"Error: {response.text}")


def test_unauthenticated_chat():
    """Test chat without authentication (should still work but not personalized)."""
    print("\n" + "=" * 70)
    print("TEST 5: Chat without authentication")
    print("=" * 70)
    
    response = requests.post(
        f"{BASE_URL}/api/chat",
        json={
            "messages": [{"role": "user", "content": "What courses are available in Computer Science?"}],
            "tools_enabled": False
        }
    )
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Reply: {data.get('reply', 'N/A')[:200]}...")
        print("\n✓ Unauthenticated chat works")
    else:
        print(f"✗ Error: {response.text}")


def run_all_tests():
    """Run all authentication tests."""
    print("\n" + "=" * 70)
    print("AUTHENTICATION & PERSONALIZATION TEST SUITE")
    print("=" * 70)
    print("\nEnsure API is running: uvicorn api.main:app --reload")
    print("Ensure database is populated: python -m utils.setup_database")
    
    try:
        # Health check
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code != 200:
            print("\n✗ API not responding. Start with: uvicorn api.main:app --reload")
            return
        
        # Run tests
        token = test_login()
        if not token:
            print("\n✗ Cannot proceed without valid token")
            return
        
        test_invalid_login()
        test_profile(token)
        test_personalized_chat(token)
        test_unauthenticated_chat()
        
        print("\n" + "=" * 70)
        print("✅ All authentication tests completed!")
        print("=" * 70)
        
    except requests.exceptions.ConnectionError:
        print("\n✗ Cannot connect to API. Start with: uvicorn api.main:app --reload")
    except Exception as e:
        print(f"\n✗ Test error: {e}")


if __name__ == "__main__":
    run_all_tests()
