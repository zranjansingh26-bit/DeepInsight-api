"""
DeepInsight Starter Suite — Billing API Routes.

Endpoints for Stripe checkout and webhooks.
"""

import logging
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from pydantic import BaseModel

from api.auth import get_current_user
from models.schemas import UserContext
from services import billing_service

logger = logging.getLogger(__name__)
router = APIRouter()

class CheckoutRequest(BaseModel):
    price_id: str
    success_url: str
    cancel_url: str

class PortalRequest(BaseModel):
    return_url: str


@router.get("/plans")
async def get_plans():
    """Return available subscription plans and their limits."""
    return billing_service.get_available_plans()


@router.post("/checkout")
async def create_checkout(
    request: CheckoutRequest,
    user: UserContext = Depends(get_current_user)
):
    """Create a Stripe checkout session."""
    if not user.email:
        # In a real app we might fetch from DB if not in token
        user.email = "placeholder@example.com"
        
    try:
        return billing_service.create_checkout_session(
            user_id=user.user_id,
            email=user.email,
            price_id=request.price_id,
            success_url=request.success_url,
            cancel_url=request.cancel_url
        )
    except Exception as e:
        logger.error(f"Checkout error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/portal")
async def create_portal(
    request: PortalRequest,
    user: UserContext = Depends(get_current_user)
):
    """Create a Stripe Customer Portal session."""
    try:
        return billing_service.create_portal_session(
            user_id=user.user_id,
            return_url=request.return_url
        )
    except Exception as e:
        logger.error(f"Portal error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/usage")
async def get_usage(user: UserContext = Depends(get_current_user)):
    """Get current period usage stats."""
    try:
        return billing_service.get_user_usage(user.user_id)
    except Exception as e:
        logger.error(f"Failed to fetch usage: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch usage data")


@router.post("/cancel")
async def cancel_subscription(user: UserContext = Depends(get_current_user)):
    """Cancel the user's subscription at period end."""
    try:
        return billing_service.cancel_subscription(user.user_id)
    except Exception as e:
        logger.error(f"Failed to cancel subscription: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/webhook")
async def stripe_webhook(request: Request):
    """Handle Stripe webhooks."""
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    
    if not sig_header:
        raise HTTPException(status_code=400, detail="Missing signature")
        
    try:
        billing_service.process_webhook(payload, sig_header)
        return Response(status_code=200)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Webhook processing error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
