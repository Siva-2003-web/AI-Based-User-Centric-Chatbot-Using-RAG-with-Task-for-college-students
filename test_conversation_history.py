"""Test script for conversation history and feedback features.

Tests:
1. Login and chat with authentication
2. Retrieve conversation history
3. Submit feedback (thumbs up/down)
4. View analytics
"""

import requests
import json

BASE_URL = "http://localhost:8000"


def test_authenticated_chat_with_history():
    """Test chat flow with conversation history tracking."""
    print("\n" + "=" * 70)
    print("TEST 1: Authenticated Chat & History Tracking")
    print("=" * 70)
    
    # Step 1: Login
    print("\n1. Logging in...")
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"student_id": "STU00001", "password": "password123"}
    )
    
    if response.status_code != 200 or not response.json().get("success"):
        print(f"✗ Login failed: {response.text}")
        return None
    
    token = response.json().get("token")
    print(f"✓ Login successful! Token: {token[:30]}...")
    
    # Step 2: Have a conversation
    print("\n2. Sending chat messages...")
    headers = {"Authorization": f"Bearer {token}"}
    
    queries = [
        "What's my schedule today?",
        "Check my attendance in CS101",
        "When is my next exam?"
    ]
    
    for query in queries:
        print(f"\n  Query: {query}")
        response = requests.post(
            f"{BASE_URL}/api/chat",
            headers=headers,
            json={
                "messages": [{"role": "user", "content": query}],
                "tools_enabled": True
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"  Reply: {data.get('reply', 'N/A')[:150]}...")
            print(f"  ✓ Conversation saved to history")
        else:
            print(f"  ✗ Error: {response.text}")
    
    return token


def test_conversation_history(token: str):
    """Test retrieving conversation history."""
    print("\n" + "=" * 70)
    print("TEST 2: Retrieve Conversation History")
    print("=" * 70)
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(
        f"{BASE_URL}/api/chat/history",
        headers=headers,
        params={"limit": 10}
    )
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"\n✓ Found {data['count']} conversations\n")
        
        for i, conv in enumerate(data['conversations'][:3], 1):
            print(f"[{i}] ID: {conv['conversation_id']}")
            print(f"    Query: {conv['user_query'][:80]}...")
            print(f"    Reply: {conv['assistant_reply'][:80]}...")
            print(f"    Time: {conv['created_at']}")
            print()
        
        return data['conversations']
    else:
        print(f"✗ Error: {response.text}")
        return []


def test_feedback(token: str, conversations: list):
    """Test submitting feedback."""
    print("\n" + "=" * 70)
    print("TEST 3: Submit Feedback")
    print("=" * 70)
    
    if not conversations:
        print("✗ No conversations to provide feedback on")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Submit positive feedback on first conversation
    conv_id = conversations[0]['conversation_id']
    print(f"\n1. Submitting 👍 (thumbs up) for conversation {conv_id}...")
    
    response = requests.post(
        f"{BASE_URL}/api/chat/feedback",
        headers=headers,
        json={
            "conversation_id": conv_id,
            "rating": 1,
            "comment": "Very helpful response!"
        }
    )
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✓ {data['message']}")
    else:
        print(f"✗ Error: {response.text}")
    
    # Submit negative feedback on second conversation
    if len(conversations) > 1:
        conv_id = conversations[1]['conversation_id']
        print(f"\n2. Submitting 👎 (thumbs down) for conversation {conv_id}...")
        
        response = requests.post(
            f"{BASE_URL}/api/chat/feedback",
            headers=headers,
            json={
                "conversation_id": conv_id,
                "rating": -1,
                "comment": "Could be more specific"
            }
        )
        
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✓ {data['message']}")
        else:
            print(f"✗ Error: {response.text}")


def test_analytics(token: str):
    """Test analytics endpoint."""
    print("\n" + "=" * 70)
    print("TEST 4: View Analytics")
    print("=" * 70)
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/api/analytics", headers=headers)
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        
        print("\n📊 Global Statistics:")
        stats = data.get('global_stats', {})
        print(f"  Total Conversations: {stats.get('total_conversations', 0)}")
        print(f"  Unique Students: {stats.get('unique_students', 0)}")
        print(f"  Positive Feedback: {stats.get('positive_feedback', 0)}")
        print(f"  Negative Feedback: {stats.get('negative_feedback', 0)}")
        print(f"  Feedback Ratio: {stats.get('feedback_ratio', 0):.2%}")
        
        if 'student_stats' in data:
            print("\n👤 Your Statistics:")
            st_stats = data['student_stats']
            print(f"  Your Conversations: {st_stats.get('total_conversations', 0)}")
            print(f"  Active Days: {st_stats.get('active_days', 0)}")
        
        print("\n🔥 Most Asked Questions (Last 30 days):")
        for i, q in enumerate(data.get('most_asked_questions', [])[:5], 1):
            print(f"  {i}. {q['question'][:70]}")
            print(f"     Frequency: {q['frequency']}, Avg Rating: {q['avg_rating']}")
        
        print("\n💬 Recent Feedback:")
        for i, fb in enumerate(data.get('recent_feedback', [])[:3], 1):
            print(f"  {i}. {fb['rating']} - {fb['user_query'][:50]}...")
            if fb.get('comment'):
                print(f"     Comment: {fb['comment']}")
        
        print("\n✓ Analytics retrieved successfully")
    else:
        print(f"✗ Error: {response.text}")


def run_all_tests():
    """Run all conversation history and feedback tests."""
    print("\n" + "=" * 70)
    print("CONVERSATION HISTORY & FEEDBACK TEST SUITE")
    print("=" * 70)
    print("\nEnsure API is running: uvicorn api.main:app --reload")
    print("Ensure database is updated: python -m utils.setup_database")
    
    try:
        # Health check
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code != 200:
            print("\n✗ API not responding. Start with: uvicorn api.main:app --reload")
            return
        
        # Run tests
        token = test_authenticated_chat_with_history()
        if not token:
            print("\n✗ Cannot proceed without authentication")
            return
        
        conversations = test_conversation_history(token)
        test_feedback(token, conversations)
        test_analytics(token)
        
        print("\n" + "=" * 70)
        print("✅ All conversation history & feedback tests completed!")
        print("=" * 70)
        
    except requests.exceptions.ConnectionError:
        print("\n✗ Cannot connect to API. Start with: uvicorn api.main:app --reload")
    except Exception as e:
        print(f"\n✗ Test error: {e}")


if __name__ == "__main__":
    run_all_tests()
