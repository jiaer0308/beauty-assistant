import requests
import os
    
BASE_URL = "http://localhost:8000/api/v1"
# Use absolute path relative to this script to be CWD-independent
TEST_DIR = os.path.dirname(os.path.abspath(__file__))
TEST_IMAGE = os.path.join(TEST_DIR, "test_image1.jpeg")
    
def test_anonymous_first_flow():
    print("--- 1. Creating Guest Session ---")
    r_guest = requests.post(f"{BASE_URL}/auth/guest")
    guest_token = r_guest.json()["guest_token"]
    print(f"Guest Token: {guest_token}")

    print("\n--- 2. Performing SCA Analysis as Guest ---")
    with open(TEST_IMAGE, "rb") as f:
        # Note: Analysis requires the X-Guest-Token header
        # and quiz_data form field (even if empty)
        files = {"file": ("image.jpg", f, "image/jpeg")}
        data = {"quiz_data": "{}"}
        headers = {"X-Guest-Token": guest_token}
        r_analyze = requests.post(f"{BASE_URL}/sca/analyze", files=files, data=data, headers=headers)
    print(f"Analysis Status: {r_analyze.status_code}")
    print(f"Detected Season: {r_analyze.json().get('result', {})}")

    print("\n--- 3. Upgrading Guest to Permanent User ---")
    # This triggers the Identity Bridge in the database
    import time
    unique_email = f"test_{int(time.time())}@example.com"
    print(f"Using email: {unique_email}")
    
    register_data = {
        "email": unique_email,
        "password": "SecurePassword123",
        "guest_token": guest_token
    }
    r_reg = requests.post(f"{BASE_URL}/auth/register", json=register_data)
    print(f"Registration: {r_reg.status_code}")
    if r_reg.status_code != 200:
        print(f"Error during registration: {r_reg.text}")
        return
        
    reg_json = r_reg.json()
    access_token = reg_json["token"]["access_token"]

    print("\n--- 4. Verifying History Migration ---")
    # The history from Step 2 should now belong to this user
    headers = {"Authorization": f"Bearer {access_token}"}
    r_hist = requests.get(f"{BASE_URL}/history/", headers=headers)

    history = r_hist.json()
    print(f"Sessions found in history: {len(history)}")
    if len(history) > 0:
        print(f"Migrated Session Season ID: {history[0]['season_id']}")

if __name__ == "__main__":
    test_anonymous_first_flow()