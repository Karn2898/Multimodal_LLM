"""
services/gemini_service.py – Low-level wrapper around the Google Generative AI SDK.

Supports text-only, image + text, and audio + text prompts.
"""

from __future__ import annotations

import google.generativeai as genai

from config.settings import settings
from utils.logger import get_logger

logger = get_logger(__name__)

# Configure the SDK once at import time
genai.configure(api_key=settings.GEMINI_API_KEY)


class GeminiService:
    """Thin wrapper around google-generativeai for multimodal requests."""

    def __init__(self, model_name: str | None = None) -> None:
        self.model_name = model_name or settings.GEMINI_MODEL
        self._model = genai.GenerativeModel(self.model_name)

    # ------------------------------------------------------------------
    # Text
    # ------------------------------------------------------------------

    async def generate_text(self, prompt: str) -> str:
        """Send a plain-text prompt and return the generated text."""
        logger.debug("Sending text prompt to Gemini model '%s'.", self.model_name)
        response = await self._model.generate_content_async(prompt)
        return response.text

    # ------------------------------------------------------------------
    # Image + Text
    # ------------------------------------------------------------------

    async def generate_with_image(self, prompt: str, image_part: dict) -> str:
        """Send an image blob and a text prompt; return the generated text."""
        logger.debug("Sending image+text prompt to Gemini model '%s'.", self.model_name)
        response = await self._model.generate_content_async([image_part, prompt])
        return response.text

    # ------------------------------------------------------------------
    # Audio + Text
    # ------------------------------------------------------------------

    async def generate_with_audio(self, prompt: str, audio_part: dict) -> str:
        """Send an audio blob and a text prompt; return the generated text."""
        logger.debug("Sending audio+text prompt to Gemini model '%s'.", self.model_name)
        response = await self._model.generate_content_async([audio_part, prompt])
        return response.text

    # ------------------------------------------------------------------
    # Multi-turn chat (text-only)
    # ------------------------------------------------------------------

    def start_chat(self, history: list[dict] | None = None) -> genai.ChatSession:
        """Start a multi-turn chat session, optionally pre-seeded with history."""
        return self._model.start_chat(history=history or [])

    async def send_message(self, session: genai.ChatSession, message: str) -> str:
        """Send a message in an existing chat session and return the reply."""
        response = await session.send_message_async(message)
        return response.text
