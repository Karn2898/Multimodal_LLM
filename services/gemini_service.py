
"""Gemini SDK wrapper for text, image, and audio interactions."""

from __future__ import annotations

from dataclasses import dataclass, field

from google import genai
from google.genai import types

from config.settings import settings
from utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class _ChatSession:
    """Small in-memory chat-session container."""

    history: list[dict] = field(default_factory=list)


class GeminiService:
    """Thin wrapper around google-genai for multimodal requests."""

    def __init__(self, model_name: str | None = None) -> None:
        self.model_name = model_name or settings.GEMINI_MODEL
        self._client = genai.Client(api_key=settings.GEMINI_API_KEY)

    async def _generate(self, contents: list) -> str:
        response = await self._client.aio.models.generate_content(
            model=self.model_name,
            contents=contents,
        )
        if not response.text:
            raise ValueError("Gemini returned an empty response.")
        return response.text

    async def generate_text(self, prompt: str) -> str:
        """Send a plain-text prompt and return the generated text."""
        logger.debug("Sending text prompt to Gemini model '%s'.", self.model_name)
        return await self._generate([prompt])

    async def generate_with_image(self, prompt: str, image_part: dict) -> str:
        """Send an image blob and a text prompt; return the generated text."""
        logger.debug("Sending image+text prompt to Gemini model '%s'.", self.model_name)
        part = types.Part.from_bytes(
            data=image_part["data"],
            mime_type=image_part["mime_type"],
        )
        return await self._generate([part, prompt])

    async def generate_with_audio(self, prompt: str, audio_part: dict) -> str:
        """Send an audio blob and a text prompt; return the generated text."""
        logger.debug("Sending audio+text prompt to Gemini model '%s'.", self.model_name)
        part = types.Part.from_bytes(
            data=audio_part["data"],
            mime_type=audio_part["mime_type"],
        )
        return await self._generate([part, prompt])

    def start_chat(self, history: list[dict] | None = None) -> _ChatSession:
        """Start a multi-turn chat session, optionally pre-seeded with history."""
        return _ChatSession(history=history or [])

    async def send_message(self, session: _ChatSession, message: str) -> str:
        """Send a message in an existing chat session and return the reply."""
        history_lines: list[str] = []
        for item in session.history:
            role = item.get("role", "user")
            parts = item.get("parts", [])
            text_parts = [p.get("text", "") for p in parts if isinstance(p, dict)]
            if text_parts:
                history_lines.append(f"{role}: {' '.join(text_parts)}")

        composed = "\n".join(history_lines + [f"user: {message}"])
        reply = await self._generate([composed])
        session.history.extend(
            [
                {"role": "user", "parts": [{"text": message}]},
                {"role": "model", "parts": [{"text": reply}]},
            ]
        )
        return reply
