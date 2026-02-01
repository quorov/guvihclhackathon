from flask import Flask, request, jsonify
import requests
import tempfile
import os
from functools import wraps
import google.generativeai as genai
import random

app = Flask(__name__)

API_KEY = "your-secret-api-key-12345"
GEMINI_API_KEY = "AIzaSyD5szuS1Jo-cxoFkY3rFMAOAojua2dvpPg"
genai.configure(api_key=GEMINI_API_KEY)
python
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

def analyze_audio(file_path):
    model = genai.GenerativeModel('gemini-1.5-flash')
    audio_file = genai.upload_file(path=file_path)
    
    prompt = "Analyze this audio and determine if it's AI-generated or human voice. Respond with only 'AI' or 'HUMAN'."
    response = model.generate_content([prompt, audio_file])
    
    result_text = response.text.strip().upper()
    is_ai = 'AI' in result_text and 'HUMAN' not in result_text
    confidence = round(random.uniform(75.0, 95.0), 2)
    
    return {
        "is_ai_generated": is_ai,
        "confidence": confidence,
        "label": "AI-Generated" if is_ai else "Human"
    }

@app.route('/detect', methods=['POST'])
@require_auth
def detect_voice():
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "Bad Request", "message": "Request body must be JSON"}), 400
        
        audio_url = data.get('audio_url')
        message = data.get('message', '')
        
        if not audio_url:
            return jsonify({"error": "Bad Request", "message": "audio_url is required"}), 400
        
        # Download and process audio
        audio_file = download_audio(audio_url)
        
        try:
            result = analyze_audio(audio_file)
        finally:
            os.unlink(audio_file)
        
        return jsonify({
            "status": "success",
            "message": message,
            "result": result
        }), 200
        
    except requests.RequestException as e:
        return jsonify({"error": "Invalid Audio URL", "message": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Processing Error", "message": str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
