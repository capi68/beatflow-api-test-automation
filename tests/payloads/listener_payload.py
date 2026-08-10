"""PAYLOAD builders for listener API requests."""

import uuid
from tests.models.listener_model import Listener

def listener_create_payload(listener: Listener = None, **overrides) -> dict:
    """Build a valid payload for POST /listeners."""
    if listener is None:
        listener = Listener()
    uid = uuid.uuid4().hex[:8]
    payload = {
        "username": listener.username or f"musiclover{uid}",
        "email": listener.email or f"listener{uid}@beatflow.com",
        "password": listener.password,
        "first_name": listener.first_name,
        "last_name": listener.last_name,
        "date_of_birth": listener.date_of_birth,
        "country": listener.country,
    }
    payload.update(overrides)

    return payload

def listener_update_payload(**kwargs) -> dict:
    """Build a payload for PUT /listeners/<id> with only the provided fields."""
    return {k: v for k, v in kwargs.items() if v is not None}

def listener_login_payload(email: str, password: str) -> dict:
    """Build payload for POST /listener/login."""
    return {"email": email, "password": password}
