

from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, HttpUrl


class RoleEnum(str, Enum):
    user = "user"
    assistant = "assistant"


class TextChatRequest(BaseModel):
   

    message: str
    history: Optional[list[dict]] = None


class ImageChatRequest(BaseModel):


    message: str
    image_url: HttpUrl
    history: Optional[list[dict]] = None


class ChatResponse(BaseModel):
 

    role: RoleEnum = RoleEnum.assistant
    content: str
    model: str


class UploadResponse(BaseModel):


    filename: str
    url: str
    content_type: str
    size_bytes: int


class ErrorResponse(BaseModel):
  

    detail: str
