# Multimodal_LLM

multimodal-gemini-app/
├── .env
├── requirements.txt
├── README.md
├── main.py                    # FastAPI entrypoint
├── config/
│   ├── settings.py            # GEMINI_API_KEY, model name, timeouts
├── api/
│   ├── __init__.py
│   ├── v1/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── routes.py          # /chat, /upload endpoints
│   │   └── models.py          # Pydantic models (text, image_url, audio_file, etc.)
├── services/
│   ├── __init__.py
│   ├── gemini_service.py      # Gemini API calls (image + text + audio)
│   ├── image_service.py       # download / validate image, prepare for Gemini
│   ├── audio_service.py       # process audio (upload, convert, send to Gemini)
│   └── orchestrator.py        # glue: image + text + audio → Gemini prompt
├── utils/
│   ├── __init__.py
│   ├── file_helpers.py        # save uploaded files, generate URLs
│   ├── security.py            # simple auth / rate limiting (optional)
│   └── logger.py              # basic logging
├── static/
│   └── uploads/
│       ├── images/
│       └── audio/
└── scripts/
    └── init_db.py             # optional DB init (for chat history)
