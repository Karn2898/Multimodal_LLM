Live app: [auroraq.onrender.com](https://auroraq.onrender.com/)

# Multimodal Gemini App

A **FastAPI** service that exposes a clean REST API for multimodal (text, image, and audio) conversations powered by **Google Gemini**.

------------------------------------------------------------------------------

## Render Deployment

This project is deployed on Render as a web service. The deployment flow is:

1. Connect the GitHub repository to Render.
2. Create a new Web Service from the repo.
3. Set the build command to install dependencies, for example `pip install -r requirements.txt`.
4. Set the start command to launch the FastAPI app on Render's assigned port, for example `uvicorn main:app --host 0.0.0.0 --port $PORT`.
5. Add the required environment variables in the Render dashboard, especially `GEMINI_API_KEY` and any optional settings you use locally.
6. Deploy the service and wait for Render to finish the build and start the app.

After deployment, the public app is available at [https://auroraq.onrender.com/](https://auroraq.onrender.com/).


## Features

- 💬 **Text chat** – multi-turn conversations via `/api/v1/chat`
- 🖼️ **Image + text** – send an image URL or upload a file with a prompt
- 🔊 **Audio + text** – upload an audio file and ask Gemini about it
- 📁 **File upload** – store images and audio in static storage and get back a URL
- 🔐 **Optional API-key auth** – bearer-token guard on every endpoint
- 📈 **Rate limiting** – configurable via environment variables
- 🗄️ **Optional chat history** – SQLite schema included (`scripts/init_db.py`)

---

## Project Structure

```
multimodal-gemini-app/
├── .env                        # Environment variables (copy from this file)
├── requirements.txt            # Python dependencies
├── README.md                   # This file
├── main.py                     # FastAPI entrypoint
├── config/
│   ├── __init__.py
│   └── settings.py             # GEMINI_API_KEY, model name, timeouts, etc.
├── api/
│   ├── __init__.py
│   └── v1/
│       ├── __init__.py
│       ├── base.py             # Shared base router
│       ├── routes.py           # /chat, /upload endpoints
│       └── models.py           # Pydantic models (TextChatRequest, ImageChatRequest, …)
├── services/
│   ├── __init__.py
│   ├── gemini_service.py       # Gemini API calls (text, image + text, audio + text)
│   ├── image_service.py        # Download / validate images, prepare for Gemini
│   ├── audio_service.py        # Validate / upload audio, prepare for Gemini
│   └── orchestrator.py         # Glue: image + text + audio → Gemini prompt
├── utils/
│   ├── __init__.py
│   ├── file_helpers.py         # Save uploaded files, generate public URLs
│   ├── security.py             # Bearer-token auth dependency
│   └── logger.py               # Centralised logging
├── static/
│   └── uploads/
│       ├── images/             # Uploaded images (git-ignored except .gitkeep)
│       └── audio/              # Uploaded audio  (git-ignored except .gitkeep)
└── scripts/
    └── init_db.py              # Optional SQLite schema init for chat history
```

---

## Quick Start

### 1. Clone & install dependencies

```bash
git clone https://github.com/Karn2898/Multimodal_LLM.git
cd Multimodal_LLM
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure environment variables

Copy the `.env` file and fill in your **Google Gemini API key**:

```bash
cp .env .env.local   # or just edit .env directly
```

| Variable | Default | Description |
|---|---|---|
| `GEMINI_API_KEY` | *(required)* | Your Google AI Studio API key |
| `GEMINI_MODEL` | `gemini-1.5-pro` | Model to use |
| `GEMINI_TIMEOUT` | `60` | Request timeout in seconds |
| `APP_HOST` | `0.0.0.0` | Uvicorn bind host |
| `APP_PORT` | `8000` | Uvicorn bind port |
| `APP_RELOAD` | `true` | Hot-reload in development |
| `MAX_IMAGE_SIZE_MB` | `10` | Maximum image upload size |
| `MAX_AUDIO_SIZE_MB` | `25` | Maximum audio upload size |
| `API_SECRET_KEY` | *(empty = disabled)* | Bearer token for auth |

### 3. (Optional) Initialise the chat-history database

```bash
python scripts/init_db.py
```

### 4. Run the server

```bash
python main.py
# or
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Open the interactive docs at **http://localhost:8000/docs**.

---

## API Endpoints

| Method | Path | Description |
|---|---|---|
| `GET` | `/` | Health check |
| `POST` | `/api/v1/chat` | Text-only chat |
| `POST` | `/api/v1/chat/image` | Image URL + text chat |
| `POST` | `/api/v1/chat/image/upload` | Uploaded image + text chat |
| `POST` | `/api/v1/chat/audio` | Uploaded audio + text chat |
| `POST` | `/api/v1/upload/image` | Upload an image file |
| `POST` | `/api/v1/upload/audio` | Upload an audio file |

### Example – text chat

```bash
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is multimodal AI?"}'
```

### Example – image chat (URL)

```bash
curl -X POST http://localhost:8000/api/v1/chat/image \
  -H "Content-Type: application/json" \
  -d '{"message": "Describe this image.", "image_url": "https://example.com/photo.jpg"}'
```

### Example – audio chat (file upload)

```bash
curl -X POST http://localhost:8000/api/v1/chat/audio \
  -F "message=Transcribe this audio." \
  -F "file=@/path/to/audio.mp3"
```

---

## License

[MIT](LICENSE)
