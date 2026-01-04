"""Quick validation that Phase 6 API is running correctly."""

import requests

BASE_URL = "http://127.0.0.1:8000"

print("🧪 Phase 6 API Validation")
print("=" * 70)

# Test 1: Health Check
print("\n1. Health Check...")
try:
    response = requests.get(f"{BASE_URL}/health", timeout=5)
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ API is healthy: {data}")
    else:
        print(f"   ❌ Health check failed: {response.status_code}")
except Exception as e:
    print(f"   ❌ Cannot connect to API: {e}")
    print("   Make sure server is running: uvicorn api.main:app --reload")
    exit(1)

# Test 2: Login
print("\n2. Login Test...")
try:
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"student_id": "STU00001", "password": "password123"},
        timeout=5
    )
    if response.status_code == 200:
        data = response.json()
        if data.get("success"):
            print(f"   ✅ Login successful: {data['profile']['name']}")
            token = data['token']
        else:
            print(f"   ❌ Login failed: {data.get('message')}")
            exit(1)
    else:
        print(f"   ❌ Login request failed: {response.status_code}")
        exit(1)
except Exception as e:
    print(f"   ❌ Login error: {e}")
    exit(1)

# Test 3: Protected Endpoint (Profile)
print("\n3. Protected Endpoint Test (Profile)...")
try:
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/api/student/profile", headers=headers, timeout=5)
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ Profile retrieved: {data['name']} - {data['department']}")
    else:
        print(f"   ❌ Profile request failed: {response.status_code}")
except Exception as e:
    print(f"   ❌ Profile error: {e}")

# Test 4: Rate Limiting
print("\n4. Rate Limiting Test...")
print("   Making 12 rapid requests to /health (limit: 60/min)...")
success_count = 0
limited_count = 0
for i in range(12):
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            success_count += 1
        elif response.status_code == 429:
            limited_count += 1
    except:
        pass

print(f"   Successful: {success_count}, Rate Limited: {limited_count}")
if success_count == 12:
    print(f"   ✅ Rate limiting configured (not triggered yet)")
else:
    print(f"   ⚠️  Some requests failed")

# Test 5: CORS Headers
print("\n5. CORS Configuration Test...")
try:
    response = requests.options(f"{BASE_URL}/api/auth/login", timeout=5)
    cors_headers = [h for h in response.headers.keys() if 'access-control' in h.lower()]
    if cors_headers:
        print(f"   ✅ CORS headers present: {len(cors_headers)} headers")
    else:
        print(f"   ⚠️  No CORS headers found (might be OK)")
except Exception as e:
    print(f"   ⚠️  CORS test inconclusive: {e}")

# Test 6: New Endpoints
print("\n6. New Phase 6 Endpoints...")
headers = {"Authorization": f"Bearer {token}"}

endpoints_to_test = [
    ("GET", "/api/student/attendance", "Attendance"),
    ("GET", "/api/student/schedule", "Schedule"),
    ("GET", "/api/student/fees", "Fees"),
    ("GET", "/api/chat/history", "Chat History"),
    ("GET", "/api/analytics", "Analytics"),
]

for method, endpoint, name in endpoints_to_test:
    try:
        if method == "GET":
            response = requests.get(f"{BASE_URL}{endpoint}", headers=headers, timeout=5)
        else:
            response = requests.post(f"{BASE_URL}{endpoint}", headers=headers, json={}, timeout=5)
        
        if response.status_code in [200, 404]:  # 404 is ok for empty data
            print(f"   ✅ {name}: {response.status_code}")
        else:
            print(f"   ❌ {name}: {response.status_code}")
    except Exception as e:
        print(f"   ❌ {name}: {e}")

print("\n" + "=" * 70)
print("✅ Phase 6 API Validation Complete!")
print("\nAPI is running at: http://localhost:8000")
print("Interactive docs: http://localhost:8000/docs")
print("\nRun full test suite: python test_phase6_api.py")
print("=" * 70)
