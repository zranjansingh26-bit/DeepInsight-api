"""
DeepInsight Starter Suite — Admin API.

Endpoints for checking system health and usage metrics.
"""

from fastapi import APIRouter, Depends
from api.auth_extension import require_role
from models.schemas import UserContext
from middleware.observability import get_metrics

router = APIRouter()

@router.get("/metrics")
async def get_system_metrics(
    user: UserContext = Depends(require_role(["admin"]))
):
    """Retrieve system observability metrics."""
    collector = get_metrics()
    return collector.get_summary()

@router.get("/health-detailed")
async def get_detailed_health(
    user: UserContext = Depends(require_role(["admin"]))
):
    """Detailed health check for all external dependencies."""
    from config import get_settings
    settings = get_settings()
    
    health = {
        "status": "healthy",
        "supabase": "configured" if settings.supabase_url else "missing",
        "redis": "configured" if settings.redis_url else "missing",
        "llm": settings.active_llm,
        "stripe": "configured" if settings.has_stripe else "missing",
        "email": "configured" if settings.has_resend or settings.gmail_user else "missing"
    }
    
    # In a full implementation, you'd ping Redis and Supabase here
    return health
