

from __future__ import annotations

import io
import ipaddress
import urllib.parse

import httpx
from PIL import Image

from config.settings import settings
from utils.logger import get_logger

logger = get_logger(__name__)

ALLOWED_MIME_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}
MAX_BYTES = settings.MAX_IMAGE_SIZE_MB * 1024 * 1024
ALLOWED_SCHEMES = {"http", "https"}


def _validate_url(url: str) -> None:

    parsed = urllib.parse.urlparse(url)

    if parsed.scheme not in ALLOWED_SCHEMES:
        raise ValueError(
            f"URL scheme '{parsed.scheme}' is not allowed. Use http or https."
        )

    hostname = parsed.hostname or ""
    if not hostname:
        raise ValueError("URL must contain a valid hostname.")

   
    try:
        addr = ipaddress.ip_address(hostname)
        if addr.is_private or addr.is_loopback or addr.is_link_local or addr.is_reserved:
            raise ValueError(f"Requests to internal/private addresses are not allowed.")
    except ValueError as exc:
     
        if "internal" in str(exc) or "private" in str(exc):
            raise
    
    blocked_hosts = {"localhost", "metadata.google.internal"}
    if hostname.lower() in blocked_hosts:
        raise ValueError(f"Requests to '{hostname}' are not allowed.")


async def download_and_prepare_image(image_url: str) -> dict:
    
    _validate_url(image_url)

    parsed = urllib.parse.urlparse(image_url)
    safe_url = urllib.parse.urlunparse(parsed)

    logger.debug("Downloading image from %s", safe_url)
    async with httpx.AsyncClient(timeout=30, follow_redirects=False) as client:
        response = await client.get(safe_url)
        response.raise_for_status()

    content_type = response.headers.get("content-type", "").split(";")[0].strip()
    if content_type not in ALLOWED_MIME_TYPES:
        raise ValueError(
            f"Unsupported image MIME type '{content_type}'. "
            f"Allowed: {ALLOWED_MIME_TYPES}"
        )

    data = response.content
    if len(data) > MAX_BYTES:
        raise ValueError(
            f"Image size ({len(data) / 1024 / 1024:.1f} MB) exceeds the "
            f"{settings.MAX_IMAGE_SIZE_MB} MB limit."
        )

    return {"mime_type": content_type, "data": data}


def prepare_image_bytes(image_bytes: bytes, mime_type: str = "image/jpeg") -> dict:
   
    if len(image_bytes) > MAX_BYTES:
        raise ValueError(
            f"Image size ({len(image_bytes) / 1024 / 1024:.1f} MB) exceeds the "
            f"{settings.MAX_IMAGE_SIZE_MB} MB limit."
        )


    try:
        Image.open(io.BytesIO(image_bytes)).verify()
    except Exception as exc:
        raise ValueError(f"Could not decode image: {exc}") from exc

    return {"mime_type": mime_type, "data": image_bytes}
