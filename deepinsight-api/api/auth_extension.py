"""
DeepInsight Starter Suite — Auth Extensions.

Provides dependencies for Role-Based Access Control (RBAC) and
Subscription/Trial validation.
"""

from datetime import datetime, timezone
from fastapi import Depends, HTTPException, Request, status
import logging

from api.auth import get_current_user
from models.schemas import UserContext
from db.client import get_service_client

logger = logging.getLogger(__name__)

async def get_current_user_with_profile(
    user: UserContext = Depends(get_current_user)
) -> UserContext:
    """Enhance user context with profile data (plan, trial status, role)."""
    # In development dummy mode, bypass real DB check for speed if needed, 
    # but for RBAC we actually need to hit the DB.
    client = get_service_client()
    try:
        result = client.table("profiles").select(
            "subscription_plan, subscription_status, trial_end, role"
        ).eq("id", user.user_id).execute()
        
        if result.data:
            profile = result.data[0]
            user.plan = profile.get("subscription_plan", "free")
            
            # Check trial status
            trial_end = profile.get("trial_end")
            if trial_end:
                # Basic ISO parsing
                try:
                    # Clean up the string for fromisoformat if needed
                    trial_end_dt = datetime.fromisoformat(trial_end.replace('Z', '+00:00'))
                    user.trial_active = datetime.now(timezone.utc) < trial_end_dt
                except Exception as e:
                    logger.warning(f"Failed to parse trial_end: {e}")
                    
            user.role = profile.get("role", "member")
            
    except Exception as e:
        logger.error(f"Failed to fetch user profile for RBAC: {e}")
        
    return user


def require_plan(min_plan: str):
    """Dependency to enforce minimum subscription plan."""
    plan_levels = {"free": 0, "starter": 1, "pro": 2, "enterprise": 3}
    
    async def _dependency(user: UserContext = Depends(get_current_user_with_profile)):
        if user.plan == "enterprise":
            return user
            
        # Allow if trial is active
        if user.trial_active:
            return user
            
        user_level = plan_levels.get(user.plan, 0)
        required_level = plan_levels.get(min_plan, 0)
        
        if user_level < required_level:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"This feature requires the {min_plan} plan. Please upgrade."
            )
        return user
        
    return _dependency


def require_role(allowed_roles: list[str]):
    """Dependency to enforce RBAC based on user role."""
    async def _dependency(user: UserContext = Depends(get_current_user_with_profile)):
        if user.role not in allowed_roles and "admin" not in allowed_roles: # admin can do everything? Let's just check explicit roles
            # Let's say admin always has access
            if user.role != "admin" and user.role not in allowed_roles:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You do not have permission to perform this action."
                )
        return user
    
    return _dependency

def require_active_subscription():
    """Dependency to ensure the user has an active subscription or trial."""
    async def _dependency(user: UserContext = Depends(get_current_user_with_profile)):
        if user.plan == "free" and not user.trial_active:
             raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Your trial has expired. Please upgrade your plan to continue using DeepInsights."
            )
        return user
    return _dependency
