

from __future__ import annotations

import google.generativeai as genai

from config.settings import settings
from utils.logger import get_logger

logger = get_logger(__name__)

ALLOWED_AUDIO_MIME_TYPES = {
    "audio/wav",
    "audio/mp3",
    "audio/mpeg",
    "audio/ogg",
    "audio/flac",
    "audio/aac",
    "audio/webm",
}

INLINE_THRESHOLD_BYTES = 4 * 1024 * 1024  # 4 MB
MAX_BYTES = settings.MAX_AUDIO_SIZE_MB * 1024 * 1024


def prepare_audio_bytes(audio_bytes: bytes, mime_type: str = "audio/mp3") -> dict:

    if mime_type not in ALLOWED_AUDIO_MIME_TYPES:
        raise ValueError(
            f"Unsupported audio MIME type '{mime_type}'. "
            f"Allowed: {ALLOWED_AUDIO_MIME_TYPES}"
        )
    if len(audio_bytes) > MAX_BYTES:
        raise ValueError(
            f"Audio size ({len(audio_bytes) / 1024 / 1024:.1f} MB) exceeds the "
            f"{settings.MAX_AUDIO_SIZE_MB} MB limit."
        )
    return {"mime_type": mime_type, "data": audio_bytes}


def upload_audio_to_gemini(audio_bytes: bytes, mime_type: str = "audio/mp3") -> genai.types.File:
 
    import os
    import tempfile

    with tempfile.NamedTemporaryFile(suffix=".tmp", delete=False) as tmp:
        tmp.write(audio_bytes)
        tmp_path = tmp.name

    try:
        logger.debug("Uploading audio to Google File API (%d bytes).", len(audio_bytes))
        uploaded = genai.upload_file(path=tmp_path, mime_type=mime_type)
        logger.debug("Audio uploaded: %s", uploaded.name)
        return uploaded
    finally:
        os.unlink(tmp_path)


def get_audio_part(audio_bytes: bytes, mime_type: str = "audio/mp3"):
    
    if len(audio_bytes) <= INLINE_THRESHOLD_BYTES:
        return prepare_audio_bytes(audio_bytes, mime_type)
    return upload_audio_to_gemini(audio_bytes, mime_type)
