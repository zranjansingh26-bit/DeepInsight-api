"""
DeepInsight — Plan-Aware Rate Limiter.

Provides plan-based rate limiting beyond the basic slowapi IP-based limiter.
"""

import logging
from fastapi import Depends, HTTPException, Request, status

from api.auth_extension import get_current_user_with_profile
from models.schemas import UserContext

logger = logging.getLogger(__name__)

# Requests per minute per plan
PLAN_RATE_LIMITS = {
    "free": {"requests_per_minute": 10, "chat_per_minute": 5, "upload_per_hour": 3},
    "starter": {"requests_per_minute": 30, "chat_per_minute": 15, "upload_per_hour": 10},
    "pro": {"requests_per_minute": 100, "chat_per_minute": 50, "upload_per_hour": 30},
    "enterprise": {"requests_per_minute": 500, "chat_per_minute": 200, "upload_per_hour": 100},
}

# Upload size limits per plan (MB)
UPLOAD_SIZE_LIMITS = {
    "free": 10,
    "starter": 50,
    "pro": 200,
    "enterprise": 500,
}


def get_upload_size_limit(plan: str) -> int:
    """Get max upload size in MB for a plan."""
    return UPLOAD_SIZE_LIMITS.get(plan, UPLOAD_SIZE_LIMITS["free"])


def check_upload_size(max_mb: int = None):
    """Dependency to enforce upload size limits based on user plan."""
    async def _dependency(
        request: Request,
        user: UserContext = Depends(get_current_user_with_profile),
    ):
        plan = "pro" if user.trial_active else user.plan
        limit_mb = max_mb or get_upload_size_limit(plan)
        
        content_length = request.headers.get("content-length")
        if content_length:
            size_mb = int(content_length) / (1024 * 1024)
            if size_mb > limit_mb:
                raise HTTPException(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    detail={
                        "error": "file_too_large",
                        "message": f"File size exceeds your {plan} plan limit of {limit_mb}MB.",
                        "limit_mb": limit_mb,
                        "plan": plan,
                    }
                )
        return user
    
    return _dependency
