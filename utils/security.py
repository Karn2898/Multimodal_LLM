

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
  
    if not settings.API_SECRET_KEY:
        return  

    if credentials is None or credentials.credentials != settings.API_SECRET_KEY:
        logger.warning("Unauthorized request from %s", request.client)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key.",
            headers={"WWW-Authenticate": "Bearer"},
        )
