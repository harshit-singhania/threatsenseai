import os
import requests
import json
import time

BASE_URL = "http://localhost:7001"
REGISTER_URL = "http://localhost:8000/api/v1/users/register"
VIDEO_DIR = "/Users/harshit/Documents/projects/ThreatSenseAI/test_videos"

def get_user_id():
    print("Registering test user...")
    try:
        response = requests.post(REGISTER_URL, json={
            "name": "Batch Tester",
            "email": f"batch_{int(time.time())}@test.com",
            "message": "Automated testing"
        })
        if response.status_code in [200, 201]:
            data = response.json()
            user_id = data['data']['user_id']
            print(f"User registered: {user_id}")
            return user_id
        else:
            print(f"Registration failed: {response.text}")
            return None
    except Exception as e:
        print(f"Connection failed: {e}")
        return None

def test_video(filepath, user_id):
    filename = os.path.basename(filepath)
    print(f"\n--- Testing {filename} ---")
    
    with open(filepath, 'rb') as f:
        files = {'video': f}
        headers = {'X-User-ID': user_id}
        
        try:
            start_time = time.time()
            response = requests.post(f"{BASE_URL}/analyze_video", files=files, headers=headers)
            duration = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                print(f"Success ({duration:.2f}s)")
                print(f"Classification: {result.get('classification')}")
                print(f"People Count: {result.get('people_count')}")
                if result.get('analyst_report'):
                    print(f"Report: {result['analyst_report'].get('summary')[:100]}...")
            else:
                print(f"Failed ({response.status_code}): {response.text}")
                
        except Exception as e:
            print(f"Error: {e}")

def main():
    user_id = get_user_id()
    if not user_id:
        # Fallback to a random UUID if node registration fails (backend might accept it if validation is loose, or just fail)
        # But actually our Flask backend validates foreign key? 
        # Wait, if we use separate DBs (which we aren't, we are sharing), then Flask needs the user in the DB.
        # So we MUST register.
        print("Cannot proceed without valid User ID.")
        return

    files = [f for f in os.listdir(VIDEO_DIR) if f.endswith('.mp4')]
    files.sort()
    
    print(f"Found {len(files)} videos.")
    
    for f in files:
        test_video(os.path.join(VIDEO_DIR, f), user_id)

if __name__ == "__main__":
    main()
