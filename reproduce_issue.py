import sys
import os
import time

# Add FlaskServer to path to allow imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'FlaskServer'))

try:
    from FlaskServer.video_processor import process_video
except ImportError as e:
    print(f"Failed to import video_processor: {e}")
    try:
        from video_processor import process_video
    except ImportError as e2:
        print(f"Failed to import video_processor again: {e2}")
        sys.exit(1)

test_videos_dir = "/Users/harshit/Documents/projects/ThreatSenseAI/test_videos"

if not os.path.exists(test_videos_dir):
    print(f"Directory not found: {test_videos_dir}")
    sys.exit(1)

print(f"Scanning videos in {test_videos_dir}...")

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
            if result.get('analyst_report'):
                if isinstance(result['analyst_report'], dict):
                    print(f"  Report Summary: {result['analyst_report'].get('summary', 'No Summary')}")
                else:
                    print(f"  Report: {result['analyst_report']}") # Fallback if it is a string
            else:
                print("  Report: None")
        except Exception as e:
            print(f"Error processing {filename}: {e}")
            import traceback
            traceback.print_exc()
