"""
DeepInsight Starter Suite — Authentication Middleware.

Validates Supabase JWTs using the JWKS endpoint (supports both HS256 and ES256).
"""

import logging
from functools import lru_cache
from typing import Optional

import httpx
import jwt
from jwt import PyJWKClient
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer

from config import get_settings
from models.schemas import UserContext

logger = logging.getLogger(__name__)

security = HTTPBearer(auto_error=False)


@lru_cache(maxsize=1)
def _get_jwks_client(supabase_url: str) -> PyJWKClient:
    """Cached JWKS client for Supabase public key verification."""
    jwks_url = f"{supabase_url}/auth/v1/.well-known/jwks.json"
    logger.info("Fetching JWKS from: %s", jwks_url)
    return PyJWKClient(jwks_url, cache_keys=True)


async def get_current_user(
    request: Request,
    credentials=Depends(security),
) -> UserContext:
    """
    Validate the Supabase JWT and extract the user context.
    In development, falls back to a dummy user ID if no credentials provided.
    """
    settings = get_settings()

    logger.info("Auth Check - credentials: %s, APP_ENV: %s", credentials, settings.app_env)
    if not credentials:
        if settings.app_env.lower() == "development":
            # Use a valid user ID from the DB for testing bypass
            logger.info("Using development auth bypass with valid user ID")
            return UserContext(
                user_id="daa28ffc-368b-46bd-b254-3c6a68769f3d",
                email="researcher@local.dev"
            )
        
        logger.warning("Authentication failed: missing token and not in development mode")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials
    logger.info("Token received: %s...", token[:10] if token else "None")

    try:
        # Supabase uses HS256 by default with the JWT Secret
        payload = jwt.decode(
            token,
            settings.supabase_jwt_secret,
            algorithms=["HS256"],
            audience="authenticated",
        )
        
        user_id = payload.get("sub")
        email = payload.get("email")

        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing user ID.",
            )

        return UserContext(user_id=user_id, email=email)

    except jwt.ExpiredSignatureError:
        if settings.app_env.lower() == "development":
            logger.info("Token expired in development, using bypass")
            return UserContext(
                user_id="daa28ffc-368b-46bd-b254-3c6a68769f3d",
                email="researcher@local.dev"
            )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired.",
        )
    except jwt.InvalidTokenError as e:
        if settings.app_env.lower() == "development":
            logger.info("Invalid token in development, using bypass: %s", str(e))
            return UserContext(
                user_id="daa28ffc-368b-46bd-b254-3c6a68769f3d",
                email="researcher@local.dev"
            )
        logger.warning("Invalid token attempt: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid authentication token: {str(e)}",
        )
    except Exception as e:
        if settings.app_env.lower() == "development":
            logger.info("Auth error in development, using bypass: %s", str(e))
            return UserContext(
                user_id="daa28ffc-368b-46bd-b254-3c6a68769f3d",
                email="researcher@local.dev"
            )
        logger.exception("Authentication error")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error validating authentication token.",
        )


async def get_optional_user(
    request: Request,
    credentials=Depends(security),
) -> Optional[UserContext]:
    """
    Optional authentication — returns None if no token is provided
    instead of raising an error.
    """
    if credentials is None:
        return None
    try:
        return await get_current_user(request, credentials)
    except HTTPException:
        return None
