# AI-Generated Voice Detection API

## Quick Start

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the API:
```bash
python app.py
```

API will be available at `http://localhost:5000`

## API Endpoint

**POST** `/detect`

### Headers
```
Authorization: your-secret-api-key-12345
```
or
```
X-API-Key: your-secret-api-key-12345
```

### Request Body
```json
{
  "audio_url": "https://example.com/audio.mp3",
  "message": "Test request description"
}
```

### Response
```json
{
  "status": "success",
  "message": "Test request description",
  "result": {
    "is_ai_generated": true,
    "confidence": 85.5,
    "label": "AI-Generated"
  }
}
```

## Testing with cURL

```bash
curl -X POST http://localhost:5000/detect \
  -H "Authorization: your-secret-api-key-12345" \
  -H "Content-Type: application/json" \
  -d '{"audio_url": "https://example.com/sample.mp3", "message": "Test"}'
```

## Deployment

For deployment (Heroku, Railway, Render):
- Update API_KEY in app.py with environment variable
- Ensure all dependencies are in requirements.txt
- Use production WSGI server (gunicorn)
