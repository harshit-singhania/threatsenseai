import cv2
import os
import numpy as np
from collections import Counter
import tempfile

# Import real prediction functions
# We assume dependencies are installed now
try:
    # Adjust path if needed based on where this file is relative to New_Model
    import sys
    sys.path.append(os.path.join(os.path.dirname(__file__), 'New_Model'))
    from predictyolo import detect_person_count
    from predict import predict_image
except ImportError as e:
    print(f"Import Error in video_processor: {e}")
    # Fallback only if absolutely necessary, but we want to fail fast if models are missing now
    def predict_image(image_path):
        return "Model Import Error"
    def detect_person_count(image_path):
        return 0

def process_video(video_path, sample_rate=30):
    """
    Process video frames to detect threats and people.
    sample_rate: Process 1 frame every 'sample_rate' frames.
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError("Could not open video file")

    frame_count = 0
    predictions = []
    max_people = 0
    
    import shutil
    from agent_manager import process_frame_with_agents

    # We will track the "most severe" result found
    # Hierarchy: Disaster > Normal
    # Temp file for the "best" frame (or last frame) to send to Gemini if needed
    best_frame_path = os.path.join(tempfile.gettempdir(), 'threat_sense_best_frame.jpg')

    # We will track the "max" people count found across all frames
    max_people_count = 0
    final_classification = "Normal"
    final_report = None
    
    # Priority: Flood/Wildfire/Earthquake > Normal
    disaster_found = False

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        if frame_count % sample_rate == 0:
            with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp:
                cv2.imwrite(tmp.name, frame)
                tmp_path = tmp.name

            try:
                # FAST PATH: Vision Agent ONLY (No Fallback)
                # We want to scan the video quickly for obvious disasters
                result = process_frame_with_agents(tmp_path, allow_fallback=False)
                
                label = result["classification"]
                count = result["people_count"]
                
                print(f"Frame {frame_count} (Vision): {label}, Count: {count}")

                if count > max_people_count:
                    max_people_count = count

                # Save this frame as a candidate for the Thinking Agent (if it's the last one we see)
                # or if it's a disaster frame, we definitely want it
                shutil.copy(tmp_path, best_frame_path)

                if label != "Normal":
                    # Vision Agent found a disaster!
                    # Trust it and break early (or continue if we want to find 'worst' disaster? usually first detection is enough)
                    # Let's verify this specific frame with the Analyst to get the report
                    print(f"Vision Agent found {label}. Getting report...")
                    # We can use the analyst directly or the manager to generate the report
                    from smart_analyst import analyst
                    report = analyst.generate_report(tmp_path, label, count)
                    
                    final_classification = label
                    final_report = report
                    disaster_found = True
                    break # Stop processing, we found the threat

            except Exception as e:
                print(f"Error processing frame {frame_count}: {e}")
            finally:
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)

        frame_count += 1

    cap.release()
    
    # SLOW PATH: If no disaster found by Vision Layer, use Thinking Agent ONCE
    # to verify the "Normal" status on the Best/Last Frame.
    if not disaster_found and os.path.exists(best_frame_path):
        print("Vision Agent saw Normal. Verifying with Thinking Agent (One-Shot)...")
        from smart_analyst import analyst
        thinking_result = analyst.analyze_scene(best_frame_path)
        
        final_classification = thinking_result["classification"]
        # Update people count if Thinking agent sees more on this frame? 
        # Or keep max from video? Let's take max of both.
        if thinking_result["people_count"] > max_people_count:
            max_people_count = thinking_result["people_count"]
            
        final_report = thinking_result["analyst_report"]
        
        # Cleanup
        os.remove(best_frame_path)
    elif os.path.exists(best_frame_path):
        os.remove(best_frame_path)

    return {
        "classification": final_classification,
        "people_count": max_people_count,
        "analyst_report": final_report
    }
