"""
api/v1/models.py – Pydantic request/response models for the Multimodal Gemini API.
"""

from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, HttpUrl


class RoleEnum(str, Enum):
    user = "user"
    assistant = "assistant"


class TextChatRequest(BaseModel):
    """Request body for a plain-text chat turn."""

    message: str
    history: Optional[list[dict]] = None


class ImageChatRequest(BaseModel):
    """Request body for an image + text chat turn (image supplied as URL)."""

    message: str
    image_url: HttpUrl
    history: Optional[list[dict]] = None


class ChatResponse(BaseModel):
    """Standard response returned by /chat endpoints."""

    role: RoleEnum = RoleEnum.assistant
    content: str
    model: str


class UploadResponse(BaseModel):
    """Response returned after a successful file upload."""

    filename: str
    url: str
    content_type: str
    size_bytes: int


class ErrorResponse(BaseModel):
    """Standard error response."""

    detail: str
