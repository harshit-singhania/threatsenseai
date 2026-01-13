import sys
import os
import time

# Add FlaskServer to path to allow imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'FlaskServer'))

try:
    from FlaskServer.video_processor import process_video
except ImportError as e:
    # Try alternate import if running from root and FlaskServer is a package
    try:
        from video_processor import process_video
    except ImportError as e2:
        print(f"Failed to import video_processor again: {e2}")
        sys.exit(1)

test_videos_dir = "/Users/harshit/Documents/projects/ThreatSenseAI/test_videos"

# Use a higher sample rate to speed up processing
SAMPLE_RATE = 150 # Check every 5 seconds (assuming 30fps)

print(f"Testing with sample_rate={SAMPLE_RATE}...")

for filename in os.listdir(test_videos_dir):
    if filename.lower().endswith(('.mp4', '.avi', '.mov')):
        video_path = os.path.join(test_videos_dir, filename)
        print(f"\nProcessing {filename}...")
        start_time = time.time()
        try:
            result = process_video(video_path)
            duration = time.time() - start_time
            print(f"Result for {filename} (took {duration:.2f}s):")
            print(f"  Classification: {result['classification']}")
            print(f"  People Count: {result['people_count']}")
        except Exception as e:
            print(f"Error processing {filename}: {e}")
