import requests
import os
import time

BASE_URL = "http://127.0.0.1:7000"
CLASSIFY_URL = f"{BASE_URL}/classify"

def test_no_file():
    print("Testing no file...")
    response = requests.post(CLASSIFY_URL)
    assert response.status_code == 400, f"Expected 400, got {response.status_code}: {response.text}"
    assert response.json()['error'] == 'No image file provided', f"Unexpected error message: {response.json()}"
    print("PASS")

def test_invalid_extension():
    print("Testing invalid extension...")
    files = {'image': ('test.txt', 'some text content', 'text/plain')}
    response = requests.post(CLASSIFY_URL, files=files)
    assert response.status_code == 400, f"Expected 400, got {response.status_code}: {response.text}"
    assert 'Invalid file type' in response.json()['error'], f"Unexpected error message: {response.json()}"
    print("PASS")

def test_valid_file_mock():
    print("Testing valid file (mock prediction)...")
    # Create a dummy image file
    with open('test_image.jpg', 'wb') as f:
        f.write(b'\xFF\xD8\xFF\xE0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xFF\xDB\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a\x1f\x1e\x1d\x1a\x1c\x1c $.\' ",#\x1c\x1c(7),01444\x1f\'9=82<.342\xFF\xC0\x00\x11\x08\x00\n\x00\n\x03\x01"\x00\x02\x11\x01\x03\x11\x01\xFF\xC4\x00\x15\x00\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x08\xFF\xDA\x00\x0c\x03\x01\x00\x02\x11\x03\x11\x00?\x00\xbf\x00\xFF\xD9')
    
    files = {'image': ('test_image.jpg', open('test_image.jpg', 'rb'), 'image/jpeg')}
    response = requests.post(CLASSIFY_URL, files=files)
    
    # Clean up
    files['image'][1].close()
    os.remove('test_image.jpg')

    if response.status_code == 200:
        print(f"PASS (Prediction: {response.json().get('label')})")
    else:
        print(f"FAIL: {response.status_code} - {response.text}")

if __name__ == "__main__":
    try:
        # Wait a bit for server to be ready if just started
        time.sleep(1)
        test_no_file()
        test_invalid_extension()
        test_valid_file_mock()
        print("\nAll tests passed!")
    except Exception as e:
        print(f"\nTest failed: {repr(e)}")
