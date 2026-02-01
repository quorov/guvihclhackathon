import requests
import json

API_URL = "http://localhost:5000/detect"
API_KEY = "your-secret-api-key-12345"

# Test with a sample audio URL
test_data = {
    "audio_url": "https://www2.cs.uic.edu/~i101/SoundFiles/BabyElephantWalk60.wav",
    "message": "Testing AI voice detection"
}

headers = {
    "Authorization": API_KEY,
    "Content-Type": "application/json"
}

response = requests.post(API_URL, json=test_data, headers=headers)

print(f"Status Code: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2)}")
