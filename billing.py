"""
Stripe subscription billing for ManTAGU Edge Telemetry.

Bank routing / account numbers are NEVER stored here.
Link your bank once in the Stripe Dashboard → Payouts / External accounts.
Stripe collects card/ACH from customers and deposits to that bank on your schedule.
"""
from __future__ import annotations

import os
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

# Optional: only required when billing is enabled
try:
    import stripe
except ImportError:  # pragma: no cover
    stripe = None  # type: ignore


# --- Suggested product tiers (map to Stripe Products/Prices in Dashboard) ---
TIERS = {
    "hobby": {
        "name": "Hobby",
        "price_usd": 0,
        "frames_per_day": 1_000,
        "regions": 1,
        "description": "Mock stream, single region, community support",
    },
    "starter": {
        "name": "Starter",
        "price_usd": 29,
        "frames_per_day": 50_000,
        "regions": 1,
        "description": "API key, production ingest, email support",
    },
    "pro": {
        "name": "Pro",
        "price_usd": 99,
        "frames_per_day": 1_000_000,
        "regions": 3,
        "description": "Multi-region, path cache, priority support",
    },
}


class CheckoutRequest(BaseModel):
    tier: str = Field(..., description="hobby | starter | pro")
    customer_email: str
    success_url: str = "https://example.com/billing/success"
    cancel_url: str = "https://example.com/billing/cancel"


class PortalRequest(BaseModel):
    customer_id: str
    return_url: str = "https://example.com/billing"


def _require_stripe() -> None:
    if stripe is None:
        raise RuntimeError(
            "stripe package not installed. Run: pip install stripe"
        )
    key = os.getenv("STRIPE_SECRET_KEY")
    if not key:
        raise RuntimeError(
            "STRIPE_SECRET_KEY is not set. "
            "Create a key in Stripe Dashboard → Developers → API keys."
        )
    stripe.api_key = key


def price_id_for_tier(tier: str) -> str:
    """
    Map logical tier → Stripe Price ID.
    Set these in env after creating Products in the Stripe Dashboard:
      STRIPE_PRICE_STARTER=price_...
      STRIPE_PRICE_PRO=price_...
    Hobby is free (no Checkout).
    """
    tier = tier.lower().strip()
    if tier == "hobby":
        raise ValueError("Hobby is free — no Checkout session needed")
    env_key = {
        "starter": "STRIPE_PRICE_STARTER",
        "pro": "STRIPE_PRICE_PRO",
    }.get(tier)
    if not env_key:
        raise ValueError(f"Unknown tier: {tier}. Use starter or pro.")
    price_id = os.getenv(env_key)
    if not price_id:
        raise RuntimeError(
            f"{env_key} is not set. Create a recurring Price in Stripe "
            "Dashboard and put its price_... id in the environment."
        )
    return price_id


def list_tiers() -> List[Dict[str, Any]]:
    return [
        {"id": k, **v, "stripe_ready": bool(os.getenv(f"STRIPE_PRICE_{k.upper()}")) if k != "hobby" else True}
        for k, v in TIERS.items()
    ]


def create_checkout_session(req: CheckoutRequest) -> Dict[str, Any]:
    """Create a Stripe Checkout Session for a subscription. Returns {url, session_id}."""
    _require_stripe()
    price_id = price_id_for_tier(req.tier)

    session = stripe.checkout.Session.create(
        mode="subscription",
        customer_email=req.customer_email,
        line_items=[{"price": price_id, "quantity": 1}],
        success_url=req.success_url + "?session_id={CHECKOUT_SESSION_ID}",
        cancel_url=req.cancel_url,
        allow_promotion_codes=True,
        billing_address_collection="auto",
        # Optional: enable ACH / bank debit where available
        payment_method_types=["card"],
        metadata={"mantagu_tier": req.tier},
    )
    return {"url": session.url, "session_id": session.id}


def create_customer_portal(req: PortalRequest) -> Dict[str, Any]:
    """Stripe Customer Portal — cancel, update card, download invoices."""
    _require_stripe()
    session = stripe.billing_portal.Session.create(
        customer=req.customer_id,
        return_url=req.return_url,
    )
    return {"url": session.url}


def construct_webhook_event(payload: bytes, sig_header: str) -> Any:
    """Verify and parse Stripe webhook. Set STRIPE_WEBHOOK_SECRET from Dashboard."""
    _require_stripe()
    secret = os.getenv("STRIPE_WEBHOOK_SECRET")
    if not secret:
        raise RuntimeError("STRIPE_WEBHOOK_SECRET is not set")
    return stripe.Webhook.construct_event(payload, sig_header, secret)


def handle_webhook_event(event: Any) -> Dict[str, str]:
    """
    Minimal handler: acknowledge important subscription events.
    Persist customer_id ↔ API key mapping in your DB for production.
    """
    etype = event["type"]
    data = event["data"]["object"]

    if etype == "checkout.session.completed":
        # data["customer"], data["subscription"], data["metadata"]["mantagu_tier"]
        return {"status": "checkout_completed", "customer": data.get("customer", "")}

    if etype in (
        "customer.subscription.updated",
        "customer.subscription.deleted",
        "invoice.paid",
        "invoice.payment_failed",
    ):
        return {"status": etype, "id": data.get("id", "")}

    return {"status": "ignored", "type": etype}
