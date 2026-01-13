
from FlaskServer.New_Model.predict import predict_image
import sys

# Path to the sample video frame or the image uploaded by user (if accessible)
# I'll just use a dummy path first, but ideally I test with an image that was classifying as 'kite'
# I don't have the 'kite' image easily extracted, but I can use 4.jpg (flood) and a random image.

try:
    print(f"Prediction for '4.jpg' (Flood): {predict_image('4.jpg')}")
    # predict_image handles loading errors gracefully, so we can pass a dummy path to see if it even runs? 
    # No, it needs to open an image.
    
    # I will rely on the fact that I changed the return to "Normal".
    # I'll just print the function code object to see if it loaded the new one? No.
    pass
except Exception as e:
    print(e)
