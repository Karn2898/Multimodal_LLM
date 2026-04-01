

from __future__ import annotations

from fastapi import UploadFile

from api.v1.models import ChatResponse
from config.settings import settings
from services.audio_service import get_audio_part
from services.gemini_service import GeminiService
from services.image_service import download_and_prepare_image, prepare_image_bytes
from utils.logger import get_logger

logger = get_logger(__name__)


class Orchestrator:


    def __init__(self) -> None:
        self._gemini = GeminiService()


    async def chat(self, message: str, history: list[dict]) -> ChatResponse:
        """Multi-turn text chat."""
        session = self._gemini.start_chat(history=history)
        reply = await self._gemini.send_message(session, message)
        return ChatResponse(content=reply, model=settings.GEMINI_MODEL)

    

    async def chat_with_image_url(
        self, message: str, image_url: str, history: list[dict]
    ) -> ChatResponse:
     
        image_part = await download_and_prepare_image(image_url)
        reply = await self._gemini.generate_with_image(message, image_part)
        return ChatResponse(content=reply, model=settings.GEMINI_MODEL)


    async def chat_with_image_file(
        self, message: str, image_file: UploadFile
    ) -> ChatResponse:
     
        image_bytes = await image_file.read()
        mime_type = image_file.content_type 
        image_part = prepare_image_bytes(image_bytes, mime_type)
        reply = await self._gemini.generate_with_image(message, image_part)
        return ChatResponse(content=reply, model=settings.GEMINI_MODEL)

   

    async def chat_with_audio(
        self, message: str, audio_file: UploadFile
    ) -> ChatResponse:
      
        audio_bytes = await audio_file.read()
        mime_type = audio_file.content_type 
        audio_part = get_audio_part(audio_bytes, mime_type)

        reply = await self._gemini.generate_with_audio(message, audio_part)
        return ChatResponse(content=reply, model=settings.GEMINI_MODEL)
