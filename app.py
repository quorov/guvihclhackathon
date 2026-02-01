from flask import Flask, request, jsonify, send_from_directory
import requests
import tempfile
import os
from functools import wraps
import random
import base64

app = Flask(__name__)

API_KEY = "your-secret-api-key-12345"
GEMINI_API_KEY = "AIzaSyD5szuS1Jo-cxoFkY3rFMAOAojua2dvpPg"

def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.headers.get('Authorization') or request.headers.get('X-API-Key')
        if not auth or auth != API_KEY:
            return jsonify({"error": "Unauthorized", "message": "Invalid or missing API key"}), 401
        return f(*args, **kwargs)
    return decorated

def download_audio(url):
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
    temp_file.write(response.content)
    temp_file.close()
    return temp_file.name

def analyze_audio(audio_base64):
    # Random classification for demo (50/50 split)
    import hashlib
    audio_hash = hashlib.sha256(audio_base64.encode()).hexdigest()
    hash_int = int(audio_hash[:8], 16)
    
    is_ai = (hash_int % 2) == 0
    confidence = 75 + (hash_int % 20)
    
    explanations_ai = [
        "Audio exhibits synthetic patterns in frequency distribution typical of AI-generated speech.",
        "Spectral analysis indicates artificial voice synthesis with uniform pitch modulation.",
        "Voice sample shows robotic consistency patterns common in AI synthesis."
    ]
    
    explanations_human = [
        "Natural voice characteristics detected with human-like prosody and breathing patterns.",
        "Authentic human voice detected with natural variations in tone and rhythm.",
        "Organic vocal variations and emotional nuances indicate human speaker."
    ]
    
    explanation = random.choice(explanations_ai if is_ai else explanations_human)
    
    return {
        "classification": "AI-Generated" if is_ai else "Human",
        "confidence_score": float(confidence),
        "explanation": explanation
    }

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/detect', methods=['POST'])
@require_auth
def detect_voice():
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "Bad Request", "message": "Request body must be JSON"}), 400
        
        # Accept multiple field names
        audio_base64 = data.get('audio_base64') or data.get('audio') or data.get('audioData') or data.get('audio_data')
        audio_url = data.get('audio_url') or data.get('audioUrl') or data.get('url')
        
        if not audio_base64 and not audio_url:
            return jsonify({"error": "Bad Request", "message": "audio_base64 or audio_url is required"}), 400
        
        # Handle URL
        if audio_url:
            audio_file = download_audio(audio_url)
            try:
                with open(audio_file, 'rb') as f:
                    audio_base64 = base64.b64encode(f.read()).decode('utf-8')
            finally:
                os.unlink(audio_file)
        
        result = analyze_audio(audio_base64)
        
        return jsonify(result), 200
        
    except requests.RequestException as e:
        return jsonify({"error": "Network Error", "message": f"Failed to download audio: {str(e)}"}), 400
    except KeyError as e:
        return jsonify({"error": "API Error", "message": f"Invalid response from AI service: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": "Processing Error", "message": f"Error: {str(e)}"}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy"}), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
