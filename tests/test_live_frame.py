
import requests
import os
import sys

BASE_URL = "http://127.0.0.1:7001"
ANALYZE_FRAME_URL = f"{BASE_URL}/analyze_frame"
# Use a local image that we know triggers detection (Flood)
TEST_IMAGE = "4.jpg" 

def test_live_frame():
    if not os.path.exists(TEST_IMAGE):
        print(f"Image {TEST_IMAGE} not found.")
        return

    print(f"Sending {TEST_IMAGE} to {ANALYZE_FRAME_URL}...")
    try:
        with open(TEST_IMAGE, 'rb') as f:
            files = {'image': (os.path.basename(TEST_IMAGE), f, 'image/jpeg')}
            response = requests.post(ANALYZE_FRAME_URL, files=files)

        if response.status_code == 200:
            data = response.json()
            print("SUCCESS: Frame processed.")
            print(f"Classification: {data.get('classification')}")
            print(f"People Count: {data.get('people_count')}")
            print(f"Analyst Report: {data.get('analyst_report')}")
            
            if data.get('classification') == 'Flood':
                 print("VERIFIED: Classification is correct.")
            else:
                 print(f"WARNING: Classification '{data.get('classification')}' expected 'Flood'.")

            if data.get('analyst_report'):
                 print("VERIFIED: Analyst report received.")
        else:
            print(f"FAILURE: Server returned {response.status_code}")
            print(response.text)

    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    test_live_frame()
