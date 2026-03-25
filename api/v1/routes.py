"""
api/v1/routes.py – Route definitions for /chat and /upload endpoints.
"""

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status

from api.v1.models import ChatResponse, ImageChatRequest, TextChatRequest, UploadResponse
from services.orchestrator import Orchestrator
from utils.file_helpers import save_upload_file
from utils.logger import get_logger
from utils.security import verify_api_key

logger = get_logger(__name__)

router = APIRouter(tags=["v1"])

# ---------------------------------------------------------------------------
# Chat endpoints
# ---------------------------------------------------------------------------


@router.post(
    "/chat",
    response_model=ChatResponse,
    summary="Text-only chat with Gemini",
)
async def chat_text(
    body: TextChatRequest,
    _: None = Depends(verify_api_key),
) -> ChatResponse:
    """Send a plain-text message to Gemini and receive a response."""
    orchestrator = Orchestrator()
    try:
        result = await orchestrator.chat(message=body.message, history=body.history or [])
    except Exception as exc:
        logger.exception("Error during text chat: %s", exc)
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc
    return result


@router.post(
    "/chat/image",
    response_model=ChatResponse,
    summary="Image + text chat with Gemini (image via URL)",
)
async def chat_image_url(
    body: ImageChatRequest,
    _: None = Depends(verify_api_key),
) -> ChatResponse:
    """Send an image URL and a text message to Gemini."""
    orchestrator = Orchestrator()
    try:
        result = await orchestrator.chat_with_image_url(
            message=body.message,
            image_url=str(body.image_url),
            history=body.history or [],
        )
    except Exception as exc:
        logger.exception("Error during image URL chat: %s", exc)
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc
    return result


@router.post(
    "/chat/image/upload",
    response_model=ChatResponse,
    summary="Image + text chat with Gemini (image via file upload)",
)
async def chat_image_upload(
    message: str = Form(...),
    file: UploadFile = File(...),
    _: None = Depends(verify_api_key),
) -> ChatResponse:
    """Upload an image file and a text message to chat with Gemini."""
    orchestrator = Orchestrator()
    try:
        result = await orchestrator.chat_with_image_file(message=message, image_file=file)
    except Exception as exc:
        logger.exception("Error during image upload chat: %s", exc)
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc
    return result


@router.post(
    "/chat/audio",
    response_model=ChatResponse,
    summary="Audio + text chat with Gemini",
)
async def chat_audio(
    message: str = Form(...),
    file: UploadFile = File(...),
    _: None = Depends(verify_api_key),
) -> ChatResponse:
    """Upload an audio file and a text message to chat with Gemini."""
    orchestrator = Orchestrator()
    try:
        result = await orchestrator.chat_with_audio(message=message, audio_file=file)
    except Exception as exc:
        logger.exception("Error during audio chat: %s", exc)
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc
    return result


# ---------------------------------------------------------------------------
# Upload endpoints
# ---------------------------------------------------------------------------


@router.post(
    "/upload/image",
    response_model=UploadResponse,
    summary="Upload an image file",
)
async def upload_image(
    file: UploadFile = File(...),
    _: None = Depends(verify_api_key),
) -> UploadResponse:
    """Upload an image to the server's static storage and return its URL."""
    try:
        info = await save_upload_file(file, sub_dir="images")
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return UploadResponse(**info)


@router.post(
    "/upload/audio",
    response_model=UploadResponse,
    summary="Upload an audio file",
)
async def upload_audio(
    file: UploadFile = File(...),
    _: None = Depends(verify_api_key),
) -> UploadResponse:
    """Upload an audio file to the server's static storage and return its URL."""
    try:
        info = await save_upload_file(file, sub_dir="audio")
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return UploadResponse(**info)
