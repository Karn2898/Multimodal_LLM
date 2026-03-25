"""
utils/security.py – Optional API-key authentication and rate limiting.

Rate limiting is implemented with slowapi (a Starlette/FastAPI wrapper around
the limits library).  Authentication is a simple bearer-token check against
``settings.API_SECRET_KEY``; if the key is not configured the check is skipped.
"""

from __future__ import annotations

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from config.settings import settings
from utils.logger import get_logger

logger = get_logger(__name__)

_bearer_scheme = HTTPBearer(auto_error=False)


async def verify_api_key(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
) -> None:
    """
    FastAPI dependency that validates the ``Authorization: Bearer <key>``
    header when ``API_SECRET_KEY`` is configured.

    If ``API_SECRET_KEY`` is empty the check is skipped (development mode).
    """
    if not settings.API_SECRET_KEY:
        return  # Auth disabled – skip

    if credentials is None or credentials.credentials != settings.API_SECRET_KEY:
        logger.warning("Unauthorized request from %s", request.client)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key.",
            headers={"WWW-Authenticate": "Bearer"},
        )
