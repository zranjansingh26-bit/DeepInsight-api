"""
DeepInsight Starter Suite — Billing Service.

Handles Stripe API integration for subscriptions, checkout sessions,
and processing webhook events.
"""

import logging
from typing import Any, Optional
import stripe

from config import get_settings
from db.client import get_service_client
from middleware.usage_middleware import get_or_create_usage, get_plan_limits

logger = logging.getLogger(__name__)

settings = get_settings()
if settings.stripe_api_key:
    stripe.api_key = settings.stripe_api_key

def get_available_plans() -> dict:
    """Return available subscription plans with their respective limits."""
    # In a real app, you might fetch active products/prices from Stripe
    return {
        "starter": {
            "name": "Starter",
            "price_monthly": 29,
            "price_yearly": 290,
            "limits": get_plan_limits("starter")
        },
        "pro": {
            "name": "Pro",
            "price_monthly": 79,
            "price_yearly": 790,
            "limits": get_plan_limits("pro")
        },
        "enterprise": {
            "name": "Enterprise",
            "price_monthly": 299,
            "price_yearly": 2990,
            "limits": get_plan_limits("enterprise")
        }
    }


def create_checkout_session(user_id: str, email: str, price_id: str, success_url: str, cancel_url: str) -> dict[str, str]:
    """Create a Stripe checkout session for a subscription."""
    if not settings.stripe_api_key:
        logger.warning("Stripe is not configured. Creating dummy checkout URL.")
        return {"checkout_url": f"{success_url}?session_id=dummy"}

    # 1. Check if user already has a Stripe Customer ID
    client = get_service_client()
    user_record = client.table("profiles").select("stripe_customer_id").eq("id", user_id).execute()
    
    customer_id = None
    if user_record.data and user_record.data[0].get("stripe_customer_id"):
        customer_id = user_record.data[0]["stripe_customer_id"]
    else:
        # Create a new customer
        customer = stripe.Customer.create(email=email, metadata={"user_id": user_id})
        customer_id = customer.id
        client.table("profiles").update({"stripe_customer_id": customer_id}).eq("id", user_id).execute()

    # 2. Create Checkout Session
    try:
        session = stripe.checkout.Session.create(
            customer=customer_id,
            payment_method_types=["card"],
            line_items=[{
                "price": price_id,
                "quantity": 1,
            }],
            mode="subscription",
            success_url=success_url,
            cancel_url=cancel_url,
            metadata={"user_id": user_id}
        )
        return {"checkout_url": session.url}
    except Exception as e:
        logger.error(f"Failed to create checkout session: {e}")
        raise RuntimeError(f"Billing system error: {str(e)}")


def create_portal_session(user_id: str, return_url: str) -> dict[str, str]:
    """Create a Stripe Customer Portal session."""
    if not settings.stripe_api_key:
         logger.warning("Stripe is not configured. Creating dummy portal URL.")
         return {"portal_url": return_url}
         
    client = get_service_client()
    user_record = client.table("profiles").select("stripe_customer_id").eq("id", user_id).execute()
    
    if not user_record.data or not user_record.data[0].get("stripe_customer_id"):
        raise ValueError("User does not have an active billing customer record.")
        
    customer_id = user_record.data[0]["stripe_customer_id"]
    
    try:
        session = stripe.billing_portal.Session.create(
            customer=customer_id,
            return_url=return_url,
        )
        return {"portal_url": session.url}
    except Exception as e:
        logger.error(f"Failed to create portal session: {e}")
        raise RuntimeError(f"Billing system error: {str(e)}")


def cancel_subscription(user_id: str) -> dict[str, str]:
    """Cancel the user's active subscription."""
    if not settings.stripe_api_key:
         return {"status": "success", "message": "Dummy cancel successful (no Stripe key)."}
         
    client = get_service_client()
    user_record = client.table("profiles").select("stripe_customer_id").eq("id", user_id).execute()
    
    if not user_record.data or not user_record.data[0].get("stripe_customer_id"):
        raise ValueError("No customer ID found.")
        
    customer_id = user_record.data[0]["stripe_customer_id"]
    
    try:
        # Find active subscriptions
        subs = stripe.Subscription.list(customer=customer_id, status="active")
        if not subs.data:
            return {"status": "success", "message": "No active subscriptions found."}
            
        for sub in subs.data:
            stripe.Subscription.modify(
                sub.id,
                cancel_at_period_end=True
            )
            
        return {"status": "success", "message": "Subscription set to cancel at end of billing period."}
    except Exception as e:
        logger.error(f"Failed to cancel subscription: {e}")
        raise RuntimeError(f"Billing system error: {str(e)}")


def get_user_usage(user_id: str) -> dict:
    """Fetch current usage stats for a user."""
    usage = get_or_create_usage(user_id)
    return {
        "period_start": usage.get("period_start"),
        "period_end": usage.get("period_end"),
        "datasets_used": usage.get("dataset_count", 0),
        "chat_messages_used": usage.get("chat_tokens", 0),
        "models_trained": usage.get("model_trainings", 0)
    }

def process_webhook(payload: bytes, sig_header: str) -> None:
    """Process incoming Stripe webhook events."""
    if not settings.stripe_webhook_secret:
        raise RuntimeError("Stripe webhook secret is not configured.")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.stripe_webhook_secret
        )
    except ValueError as e:
        logger.error("Invalid webhook payload")
        raise ValueError("Invalid payload")
    except stripe.error.SignatureVerificationError as e:
        logger.error("Invalid webhook signature")
        raise ValueError("Invalid signature")

    client = get_service_client()

    if event.type == "checkout.session.completed":
        session = event.data.object
        user_id = session.metadata.get("user_id")
        
        # Retrieve subscription to get period dates
        if session.subscription and user_id:
            subscription = stripe.Subscription.retrieve(session.subscription)
            _update_subscription_in_db(client, user_id, subscription)

    elif event.type in ["customer.subscription.updated", "customer.subscription.deleted"]:
        subscription = event.data.object
        # Need to find the user via customer ID
        customer_id = subscription.customer
        user_record = client.table("profiles").select("id").eq("stripe_customer_id", customer_id).execute()
        
        if user_record.data:
            user_id = user_record.data[0]["id"]
            _update_subscription_in_db(client, user_id, subscription)
            
    elif event.type == "invoice.payment_failed":
        invoice = event.data.object
        customer_id = invoice.customer
        user_record = client.table("profiles").select("id").eq("stripe_customer_id", customer_id).execute()
        
        if user_record.data:
            user_id = user_record.data[0]["id"]
            client.table("profiles").update({
                "subscription_status": "past_due"
            }).eq("id", user_id).execute()
    
    logger.info(f"Processed webhook event: {event.type}")


def _update_subscription_in_db(client, user_id: str, subscription: Any) -> None:
    """Helper to update user profile based on Stripe subscription state."""
    from datetime import datetime, timezone
    
    status = subscription.status
    current_period_end = datetime.fromtimestamp(subscription.current_period_end, tz=timezone.utc).isoformat()
    
    # Simple mapping based on price ID (in a real app, use a dict lookup or product metadata)
    # We will assume if we got an update, it's pro unless we inspect product
    plan = "pro" 
    
    if status == "canceled":
        plan = "free"
    
    client.table("profiles").update({
        "subscription_status": status,
        "subscription_plan": plan,
        "current_period_end": current_period_end
    }).eq("id", user_id).execute()
    logger.info(f"Updated subscription for {user_id} to {status} ({plan})")
