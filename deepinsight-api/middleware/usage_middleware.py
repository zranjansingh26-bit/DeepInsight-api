"""
DeepInsight — Usage Tracking Middleware.

Provides dependencies to check and enforce plan-based usage limits
before resource-consuming operations.
"""

import logging
from datetime import datetime, timezone
from fastapi import Depends, HTTPException, status

from api.auth import get_current_user
from api.auth_extension import get_current_user_with_profile
from models.schemas import UserContext
from db.client import get_service_client

logger = logging.getLogger(__name__)

# ── Plan Limits ──────────────────────────────────────────────
PLAN_LIMITS = {
    "free": {
        "datasets": 3,
        "chat_messages": 50,
        "model_trainings": 5,
        "reports": 5,
        "max_upload_mb": 10,
        "document_uploads": 3,
    },
    "starter": {
        "datasets": 20,
        "chat_messages": 500,
        "model_trainings": 50,
        "reports": 30,
        "max_upload_mb": 50,
        "document_uploads": 20,
    },
    "pro": {
        "datasets": 100,
        "chat_messages": 5000,
        "model_trainings": 500,
        "reports": 200,
        "max_upload_mb": 200,
        "document_uploads": 100,
    },
    "enterprise": {
        "datasets": 999999,
        "chat_messages": 999999,
        "model_trainings": 999999,
        "reports": 999999,
        "max_upload_mb": 500,
        "document_uploads": 999999,
    },
}


def get_plan_limits(plan: str) -> dict:
    """Get usage limits for a subscription plan."""
    return PLAN_LIMITS.get(plan, PLAN_LIMITS["free"])


def get_current_period_bounds() -> tuple[str, str]:
    """Get the current billing period (1st of month to end of month)."""
    now = datetime.now(timezone.utc)
    period_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    # Next month 1st
    if now.month == 12:
        period_end = now.replace(year=now.year + 1, month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
    else:
        period_end = now.replace(month=now.month + 1, day=1, hour=0, minute=0, second=0, microsecond=0)
    
    return period_start.isoformat(), period_end.isoformat()


def get_or_create_usage(user_id: str) -> dict:
    """Get or create usage metrics for the current period."""
    client = get_service_client()
    period_start, period_end = get_current_period_bounds()
    
    try:
        result = client.table("usage_metrics").select("*").eq(
            "user_id", user_id
        ).eq("period_start", period_start).execute()
        
        if result.data:
            return result.data[0]
        
        # Create new usage record
        import uuid
        record = {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "period_start": period_start,
            "period_end": period_end,
            "dataset_count": 0,
            "chat_tokens": 0,
            "model_trainings": 0,
        }
        insert_result = client.table("usage_metrics").insert(record).execute()
        return insert_result.data[0] if insert_result.data else record
    except Exception as e:
        logger.error("Failed to get/create usage metrics: %s", e)
        # Return empty — don't block the user
        return {"dataset_count": 0, "chat_tokens": 0, "model_trainings": 0}


def increment_usage(user_id: str, resource_type: str, amount: int = 1) -> None:
    """Increment a usage counter for the current period."""
    client = get_service_client()
    usage = get_or_create_usage(user_id)
    
    field_map = {
        "datasets": "dataset_count",
        "chat_messages": "chat_tokens",
        "model_trainings": "model_trainings",
    }
    
    field = field_map.get(resource_type)
    if not field:
        return
    
    try:
        new_value = usage.get(field, 0) + amount
        client.table("usage_metrics").update(
            {field: new_value, "updated_at": datetime.now(timezone.utc).isoformat()}
        ).eq("id", usage["id"]).execute()
    except Exception as e:
        logger.error("Failed to increment usage for %s: %s", user_id, e)


def check_usage_limit(resource_type: str):
    """
    FastAPI dependency that checks whether the user has exceeded
    their plan's usage limit for a given resource type.
    """
    async def _dependency(user: UserContext = Depends(get_current_user_with_profile)):
        # Trial users get Pro-level limits
        plan = "pro" if user.trial_active else user.plan
        limits = get_plan_limits(plan)
        
        max_allowed = limits.get(resource_type, 0)
        usage = get_or_create_usage(user.user_id)
        
        field_map = {
            "datasets": "dataset_count",
            "chat_messages": "chat_tokens",
            "model_trainings": "model_trainings",
        }
        
        field = field_map.get(resource_type, resource_type)
        current = usage.get(field, 0)
        
        if current >= max_allowed:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail={
                    "error": "usage_limit_exceeded",
                    "message": f"You've reached your {plan} plan limit for {resource_type} ({max_allowed}/month). Please upgrade.",
                    "current": current,
                    "limit": max_allowed,
                    "plan": plan,
                }
            )
        return user
    
    return _dependency
