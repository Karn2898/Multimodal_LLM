

from __future__ import annotations

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


def get_audio_part(audio_bytes: bytes, mime_type: str = "audio/mp3"):
    """Return validated audio payload for Gemini request construction."""
    return prepare_audio_bytes(audio_bytes, mime_type)
