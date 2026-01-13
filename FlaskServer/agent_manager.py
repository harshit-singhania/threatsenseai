
import sys
import os

# Ensure New_Model is in path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'New_Model'))

try:
    from predict import predict_image
    from predictyolo import detect_person_count
except ImportError as e:
    print(f"Agent Manager Import Error: {e}")

from smart_analyst import analyst

def process_frame_with_agents(image_path, allow_fallback=True):
    """
    Orchestrates the Dual-Agent pipeline:
    1. Vision Agent (ViT + YOLO) -> Fast, cheap.
    2. Thinking Agent (Gemini) -> Slow, capable fallback.
    """
    
    # --- STEP 1: VISION AGENT ---
    print("--- Vision Agent Active ---")
    vision_label = predict_image(image_path)
    vision_count = detect_person_count(image_path)
    
    print(f"Vision Agent Result: Label={vision_label}, Count={vision_count}")
    
    # If Vision Agent finds a threat, trust it (it's tuned for high precision on proxies)
    if vision_label != "Normal":
        # Generate report for the detected threat
        report = analyst.generate_report(image_path, vision_label, vision_count)
        return {
            "classification": vision_label,
            "people_count": vision_count,
            "analyst_report": report,
            "source": "Vision Agent"
        }
        
    # --- STEP 2: THINKING AGENT (Fallback) ---
    # Only if fallback is allowed
    if not allow_fallback:
        return {
            "classification": "Normal",
            "people_count": vision_count,
            "analyst_report": None,
            "source": "Vision Agent"
        }

    # If Vision Agent says logical "Normal", we verify with Thinking Agent
    print("--- Thinking Agent Active (Fallback) ---")
    thinking_result = analyst.analyze_scene(image_path)
    
    # Merge results
    return {
        "classification": thinking_result["classification"],
        "people_count": thinking_result["people_count"],
        "analyst_report": thinking_result["analyst_report"],
        "source": "Thinking Agent"
    }
