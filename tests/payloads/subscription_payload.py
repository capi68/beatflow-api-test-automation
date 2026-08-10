"""Payload builders for subscription API requests."""

from tests.models.subscription_model import Subscription

def subscription_create_payload(subscription: Subscription = None, listener_id: int = None, **overrides) -> dict:
    """Build a valid payload for  POST /subscriptions."""

    if subscription is None:
        subscription = Subscription()
    payload = {
        "listener_id": listener_id or subscription.listener_id,
        "plan": subscription.plan,
    }
    payload.update(overrides)

    return payload

def subscription_update_payload(**kwargs) -> dict:
    """Build a payload for PUT /subscriptions/<id> with only provide fields."""
    return {k: v for k, v in kwargs.items() if v is not None}