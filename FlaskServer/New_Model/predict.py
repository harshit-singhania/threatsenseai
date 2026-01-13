
import logging
from transformers import ViTImageProcessor, ViTForImageClassification
from PIL import Image
import torch

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load model and processor globally to avoid reloading on every request
try:
    processor = ViTImageProcessor.from_pretrained('google/vit-base-patch16-224')
    model = ViTForImageClassification.from_pretrained('google/vit-base-patch16-224')
    logger.info("ViT model loaded successfully.")
except Exception as e:
    logger.error(f"Failed to load ViT model: {e}")
    model = None
    processor = None

# Mapping ImageNet classes to Disaster Categories
# Keys are indices or label substrings (will be checked against predicted label text)
DISASTER_MAPPING = {
    "Wildfire": ["volcano", "fire_screen", "lighter", "torch"],
    "Flood": ["lakeside", "sandbar", "seashore", "canoe", "dam", "gondola", "boathouse"],
    "Earthquake": ["wreck", "cliff", "rubble", "ruins"]  # Note: 'ruins' isn't a standard class but 'wreck' is (900)
}

def predict_path(image_path):
    """
    Predicts the class of an image using ViT and maps it to disaster categories.
    """
    if model is None or processor is None:
        return "Model Load Error"

    try:
        image = Image.open(image_path)
    except Exception as e:
        logger.error(f"Error opening image {image_path}: {e}")
        return "Image Load Error"

    try:
        inputs = processor(images=image, return_tensors="pt")
        with torch.no_grad():
            outputs = model(**inputs)
        
        logits = outputs.logits
        # Get top 5 predictions to check for disaster proxies
        top5_prob, top5_indices = torch.topk(logits, 5)
        
        detected_disaster = None
        top_label = model.config.id2label[top5_indices[0][0].item()]

        # Check top 5 for any disaster proxies
        for i in range(5):
            idx = top5_indices[0][i].item()
            label = model.config.id2label[idx].lower()
            
            for disaster, proxies in DISASTER_MAPPING.items():
                for proxy in proxies:
                    if proxy in label:
                        # Found a potential disaster
                        detected_disaster = disaster
                        logger.info(f"Disaster detected via proxy '{label}' -> {disaster}")
                        break
                if detected_disaster: break
            if detected_disaster: break
            
        if detected_disaster:
            return detected_disaster
        
        return "Normal"

    except Exception as e:
        logger.error(f"Prediction error: {e}")
        return "Prediction Error"

def predict_image(image_path):
    # Wrapper to match expected signature
    return predict_path(image_path)

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        print(predict_image(sys.argv[1]))
    else:
        print("Usage: python predict.py <image_path>")
