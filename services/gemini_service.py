

from __future__ import annotations

import google.generativeai as genai

from config.settings import settings
from utils.logger import get_logger

logger = get_logger(__name__)


genai.configure(api_key=settings.GEMINI_API_KEY)


class GeminiService:
  ""

    def __init__(self, model_name):
        self.model_name = settings.GEMINI_MODEL
        self._model = genai.GenerativeModel(self.model_name)


    async def generate_text(self, prompt: str) -> str:
        logger.debug("Sending text prompt to Gemini model '%s'.", self.model_name)
        response = await self._model.generate_content_async(prompt)
        return response.text


    async def generate_with_image(self, prompt: str, image_part: dict) -> str:
       
        logger.debug("Sending image+text prompt to Gemini model '%s'.", self.model_name)
        response = await self._model.generate_content_async([image_part, prompt])
        return response.text


    async def generate_with_audio(self, prompt: str, audio_part: dict) -> str:
        
        logger.debug("Sending audio+text prompt to Gemini model '%s'.", self.model_name)
        response = await self._model.generate_content_async([audio_part, prompt])
        return response.text



    def start_chat(self, history: list[genai.types.ChatMessage] | None = None) -> genai.ChatSession:
        return self._model.start_chat(history=history)

    async def send_message(self, session: genai.ChatSession, message: str) -> str:
        
        response = await session.send_message_async(message)
        return response.text
