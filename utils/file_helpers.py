from __future__ import annotations

import os
import uuid
from pathlib import Path

import aiofiles
from fastapi import UploadFile

from config.settings import settings
from utils.logger import get_logger

logger = get_logger(__name__)

_BASE_UPLOAD_DIR = Path(settings.UPLOAD_DIR)


async def save_upload_file(
    upload_file: UploadFile,
    sub_dir: str = "",
) -> dict:
    
    dest_dir = _BASE_UPLOAD_DIR / sub_dir
    dest_dir.mkdir(parents=True, exist_ok=True)

    original_name = upload_file.filename 
    unique_name = f"{uuid.uuid4().hex}_{original_name}"
    dest_path = dest_dir / unique_name

    content = await upload_file.read()
    async with aiofiles.open(dest_path, "wb") as f:
        await f.write(content)

    url = f"/static/uploads/{sub_dir}/{unique_name}" if sub_dir else f"/static/uploads/{unique_name}"
    logger.debug("Saved upload to %s", dest_path)

    return {
        "filename": unique_name,
        "url": url,
        "content_type": upload_file.content_type or "application/octet-stream",
        "size_bytes": len(content),
    }


def generate_file_url(filename: str, sub_dir: str = "") -> str:
    """Build the public URL for a previously saved file."""
    if sub_dir:
        return f"/static/uploads/{sub_dir}/{filename}"
    return f"/static/uploads/{filename}"
