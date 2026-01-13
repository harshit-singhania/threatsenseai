
import requests
import os
import time
import sys

BASE_URL = "http://127.0.0.1:7001"
ANALYZE_VIDEO_URL = f"{BASE_URL}/analyze_video"
VIDEO_PATH = "sample_video.mp4"

def test_integration():
    if not os.path.exists(VIDEO_PATH):
        print(f"Video file {VIDEO_PATH} not found.")
        return

    print(f"Uploading {VIDEO_PATH} to {ANALYZE_VIDEO_URL}...")
    try:
        with open(VIDEO_PATH, 'rb') as f:
            files = {'video': (os.path.basename(VIDEO_PATH), f, 'video/mp4')}
            response = requests.post(ANALYZE_VIDEO_URL, files=files)

        if response.status_code == 200:
            data = response.json()
            print("SUCCESS: Video processed.")
            print(f"Classification: {data.get('classification')}")
            print(f"People Count: {data.get('people_count')}")
            print(f"Analyst Report: {data.get('analyst_report')}")
            
            # Assertions
            if data.get('classification') == 'Normal':
                 print("VERIFIED: Classification is 'Normal' (irrelevant class filtered).")
            else:
                 print(f"WARNING: Classification '{data.get('classification')}' should be 'Normal'.")

            report = data.get('analyst_report')
            if report and "Missing API Key" not in str(report):
                 print("VERIFIED: Smart Analyst generated a report (API Key worked).")
            else:
                 print("WARNING: Smart Analyst failed or missing API key.")

        else:
            print(f"FAILURE: Server returned {response.status_code}")
            print(response.text)

    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    test_integration()
