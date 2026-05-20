import requests
import json
import os

BASE_URL = "http://127.0.0.1:5000/api"
PHONE = "9999999999"

print(f"--- 1. Sending OTP to {PHONE} ---")
r = requests.post(f"{BASE_URL}/mobile-auth/send-otp", json={"phone": PHONE})
assert r.status_code == 200, f"Failed to send OTP: {r.text}"
data = r.json()
otp = data.get("otp")
print(f"Success! Received Dev OTP: {otp}")

print(f"\n--- 2. Verifying OTP ---")
r2 = requests.post(f"{BASE_URL}/mobile-auth/verify-otp", json={"phone": PHONE, "otp": otp})
assert r2.status_code == 200, f"Failed to verify OTP: {r2.text}"
user_id = r2.json().get("user_id")
print(f"Success! Verified user_id: {user_id}")

print(f"\n--- 3. Saving Profile ---")
profile_payload = {
    "user_id": user_id,
    "income": 50000,
    "expenses": 20000,
    "savings_rate": 60,
    "total_debt": 0
}
r3 = requests.post(f"{BASE_URL}/save-profile", json=profile_payload)
assert r3.status_code == 200, f"Failed to save profile: {r3.text}"
health_score = r3.json().get("health_score")
print(f"Success! Profile saved. Health Score computed: {health_score}")

print(f"\n--- 4. Checking JSON File ---")
PROFILES_FILE = os.path.join(os.path.dirname(__file__), 'data', 'profiles.json')
if os.path.exists(PROFILES_FILE):
    with open(PROFILES_FILE, 'r') as f:
        profiles = json.load(f)
        profile = profiles.get(user_id)
        if profile:
            print("Found Profile in profiles.json!")
            print(json.dumps(profile, indent=2))
        else:
            print("Profile NOT found in JSON DB!")
else:
    print(f"File {PROFILES_FILE} does not exist!")
