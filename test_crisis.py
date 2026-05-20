import requests
import json

url = "http://127.0.0.1:5000/api/chat"
ctx = {"income": 25000, "expenses": 20000, "savings_rate": 5}

print("=" * 60)
print("TEST 1: FlyCash + blackmail + 2am")
print("Expected: Emergency + blacklist_warning")
print("=" * 60)
r1 = requests.post(url, json={
    "message": "I borrowed from FlyCash at 2am and now they are blackmailing me",
    "context": ctx, "history": []
})
d1 = r1.json()
print(f"Status: {r1.status_code}")
print(f"crisis_level: {d1.get('crisis_level')}")
print(f"suggested_action: {d1.get('suggested_action')}")
print(f"blacklist_warning: {json.dumps(d1.get('blacklist_warning'), indent=2)}")
print(f"hotlines present: {bool(d1.get('hotlines'))}")
result1 = "PASS" if d1.get("crisis_level") == "Emergency" else "FAIL"
print(f">>> RESULT: {result1}")

print()
print("=" * 60)
print("TEST 2: KreditBee loan")
print("Expected: Alert + blacklist_warning")
print("=" * 60)
r2 = requests.post(url, json={
    "message": "I took a loan from KreditBee",
    "context": ctx, "history": []
})
d2 = r2.json()
print(f"Status: {r2.status_code}")
print(f"crisis_level: {d2.get('crisis_level')}")
print(f"blacklist_warning: {json.dumps(d2.get('blacklist_warning'), indent=2)}")
print(f"crisis_warning: {json.dumps(d2.get('crisis_warning'), indent=2)}")
has_bw = d2.get("blacklist_warning") is not None
result2 = "PASS" if has_bw else "FAIL"
print(f">>> RESULT: {result2}")

print()
print("=" * 60)
print("TEST 3: Normal message")
print("Expected: Normal, no warnings")
print("=" * 60)
r3 = requests.post(url, json={
    "message": "How do I save money?",
    "context": {"income": 50000, "expenses": 20000, "savings_rate": 60},
    "history": []
})
d3 = r3.json()
print(f"Status: {r3.status_code}")
print(f"crisis_level: {d3.get('crisis_level')}")
print(f"blacklist_warning: {d3.get('blacklist_warning')}")
print(f"crisis_warning: {d3.get('crisis_warning')}")
is_normal = d3.get("crisis_level") == "Normal" and d3.get("blacklist_warning") is None
result3 = "PASS" if is_normal else "FAIL"
print(f">>> RESULT: {result3}")

print()
print("=" * 60)
print(f"SUMMARY: T1={result1} | T2={result2} | T3={result3}")
print("=" * 60)
