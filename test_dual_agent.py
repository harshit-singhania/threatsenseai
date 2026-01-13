
import requests
import os
import sys
import time

BASE_URL = "http://127.0.0.1:7001"
ANALYZE_VIDEO_URL = f"{BASE_URL}/analyze_video"
TEST_VIDEO = "non_threat.mp4" # Created from sample_video.mp4

def test_fallback():
    if not os.path.exists(TEST_VIDEO):
        print(f"Video {TEST_VIDEO} not found.")
        return

    print(f"Uploading {TEST_VIDEO} to {ANALYZE_VIDEO_URL}...")
    print("Expected behavior: Vision Agent returns Normal -> Thinking Agent activates -> Returns result.")
    
    try:
        with open(TEST_VIDEO, 'rb') as f:
            files = {'video': (os.path.basename(TEST_VIDEO), f, 'video/mp4')}
            # Increased timeout as Gemini analysis per frame ensures it takes time
            response = requests.post(ANALYZE_VIDEO_URL, files=files, timeout=60)

        if response.status_code == 200:
            data = response.json()
            print("SUCCESS: Video processed.")
            print(f"Classification: {data.get('classification')}")
            print(f"People Count: {data.get('people_count')}")
            # We check if 'analyst_report' is present even if classification is Normal (or if Thinking Agent upgraded it)
            # Actually, my code only returns report if clas != Normal in analyze_scene.
            # But if Thinking Agent says "Normal", report is None. 
            # So verification: If it's truly normal, we expect Normal and people count.
            # If Thinking Agent hallucinates a disaster, we'd see it here.
            
            print(f"Analyst Report: {data.get('analyst_report')}")
        else:
            print(f"FAILURE: Server returned {response.status_code}")
            print(response.text)

    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    # Wait for server to start
    time.sleep(5)
    test_fallback()
