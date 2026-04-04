from __future__ import annotations

import asyncio
import uuid
from pathlib import Path

import aiofiles
from fastapi import UploadFile

from config.settings import settings
from utils.logger import get_logger

logger = get_logger(__name__)

_BASE_UPLOAD_DIR = Path(settings.UPLOAD_DIR)


def _is_cloudinary_configured() -> bool:
    return all(
        [
            settings.CLOUDINARY_CLOUD_NAME,
            settings.CLOUDINARY_API_KEY,
            settings.CLOUDINARY_API_SECRET,
        ]
    )


def _should_use_cloudinary() -> bool:
    backend = settings.FILE_STORAGE_BACKEND.strip().lower()

    if backend == "cloudinary":
        if not _is_cloudinary_configured():
            raise ValueError(
                "Cloudinary backend selected but credentials are missing. "
                "Set CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY and CLOUDINARY_API_SECRET."
            )
        return True

    if backend == "local":
        return False

    return settings.APP_ENV.strip().lower() == "production" and _is_cloudinary_configured()


async def _save_to_cloudinary(
    upload_file: UploadFile,
    sub_dir: str = "",
) -> dict:
    try:
        import cloudinary
        import cloudinary.uploader
    except ImportError as exc:
        raise ValueError(
            "Cloudinary package not installed. Add 'cloudinary' to requirements."
        ) from exc

    cloudinary.config(
        cloud_name=settings.CLOUDINARY_CLOUD_NAME,
        api_key=settings.CLOUDINARY_API_KEY,
        api_secret=settings.CLOUDINARY_API_SECRET,
        secure=True,
    )

    original_name = upload_file.filename or "upload.bin"
    unique_name = f"{uuid.uuid4().hex}_{original_name}"

    cloud_folder = settings.CLOUDINARY_FOLDER.strip("/")
    if sub_dir:
        cloud_folder = f"{cloud_folder}/{sub_dir.strip('/')}"

    content = await upload_file.read()

    upload_result = await asyncio.to_thread(
        cloudinary.uploader.upload,
        content,
        folder=cloud_folder,
        public_id=Path(unique_name).stem,
        resource_type="auto",
        use_filename=True,
        unique_filename=False,
        overwrite=False,
    )

    url = upload_result.get("secure_url") or upload_result.get("url")
    if not url:
        raise ValueError("Cloudinary upload failed: URL not returned.")

    logger.debug("Saved upload to Cloudinary folder=%s public_id=%s", cloud_folder, upload_result.get("public_id"))

    return {
        "filename": upload_result.get("public_id", unique_name),
        "url": url,
        "content_type": upload_file.content_type or "application/octet-stream",
        "size_bytes": len(content),
    }


async def _save_to_local(
    upload_file: UploadFile,
    sub_dir: str = "",
) -> dict:
    dest_dir = _BASE_UPLOAD_DIR / sub_dir
    dest_dir.mkdir(parents=True, exist_ok=True)

    original_name = upload_file.filename or "upload.bin"
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


async def save_upload_file(
    upload_file: UploadFile,
    sub_dir: str = "",
) -> dict:
    if _should_use_cloudinary():
        return await _save_to_cloudinary(upload_file=upload_file, sub_dir=sub_dir)
    return await _save_to_local(upload_file=upload_file, sub_dir=sub_dir)


def generate_file_url(filename: str, sub_dir: str = "") -> str:
    """Build the public URL for a previously saved file."""
    if sub_dir:
        return f"/static/uploads/{sub_dir}/{filename}"
    return f"/static/uploads/{filename}"
