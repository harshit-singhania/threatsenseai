import requests
import os
import sys

BASE_URL = "http://127.0.0.1:7001"
ANALYZE_VIDEO_URL = f"{BASE_URL}/analyze_video"

test_videos_dir = "/Users/harshit/Documents/projects/ThreatSenseAI/test_videos"

if not os.path.exists(test_videos_dir):
    print(f"Directory not found: {test_videos_dir}")
    sys.exit(1)

print(f"Testing API at {ANALYZE_VIDEO_URL} with videos in {test_videos_dir}...")

for filename in os.listdir(test_videos_dir):
    if filename.lower().endswith(('.mp4', '.avi', '.mov')):
        video_path = os.path.join(test_videos_dir, filename)
        print(f"\nUploading {filename}...")
        
        try:
            with open(video_path, 'rb') as f:
                # Add a timeout of 60 seconds
                files = {'video': (filename, f, 'video/mp4')}
                # Assuming user_id is optional or we can send a dummy one
                data = {'user_id': 'test_script'}
                
                response = requests.post(ANALYZE_VIDEO_URL, files=files, data=data, timeout=120)

            if response.status_code == 200:
                data = response.json()
                print("PASS: Request successful")
                print(f"  Classification: {data.get('classification')}")
                print(f"  People Count: {data.get('people_count')}")
                if data.get('analyst_report'):
                    summary = data['analyst_report'].get('summary') if isinstance(data['analyst_report'], dict) else data['analyst_report']
                    print(f"  Report Summary: {summary}")
                else:
                    print("  Report: None")
            else:
                print(f"FAIL: Status {response.status_code}")
                print(f"  Response: {response.text}")
                
        except Exception as e:
            print(f"Error testing {filename}: {e}")
