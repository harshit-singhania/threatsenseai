import requests
import os
import cv2
import numpy as np
import time

BASE_URL = "http://127.0.0.1:7001"
ANALYZE_VIDEO_URL = f"{BASE_URL}/analyze_video"

def create_dummy_video(filename="test_video.mp4", duration=2, fps=30):
    """Creates a dummy video file."""
    height, width = 480, 640
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(filename, fourcc, fps, (width, height))

    for _ in range(duration * fps):
        # Create a random frame
        frame = np.random.randint(0, 255, (height, width, 3), dtype=np.uint8)
        out.write(frame)

    out.release()
    print(f"Created dummy video: {filename}")

def test_video_analysis():
    print("Testing video analysis...")
    
    # List of videos to test
    video_files = [
        "sample_vids/earthquake.mp4",
        "sample_vids/flood.mp4",
        "sample_vids/wildfire.mp4"
    ]

    for video_filename in video_files:
        if not os.path.exists(video_filename):
            print(f"Skipping {video_filename} (not found)")
            continue
            
        print(f"\nAnalyzing {video_filename}...")
        try:
            with open(video_filename, 'rb') as f:
                files = {'video': (os.path.basename(video_filename), f, 'video/mp4')}
                response = requests.post(ANALYZE_VIDEO_URL, files=files)

            if response.status_code == 200:
                data = response.json()
                print("PASS")
                print(f"Response: {data}")
            else:
                print(f"FAIL: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"Error testing {video_filename}: {e}")

if __name__ == "__main__":
    try:
        # Wait a bit for server to be ready if just started
        time.sleep(1)
        test_video_analysis()
    except Exception as e:
        print(f"\nTest failed: {repr(e)}")
