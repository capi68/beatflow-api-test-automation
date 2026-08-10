"""Payload builders for License API requests."""

import uuid
from tests.models.license_model import License

def license_create_payload(licence: License = None, track_id: int = None, **overrides) -> dict:
    """Build a valid payload for POST /licenses."""

    if licence is None:
        licence = License()

    uid = uuid.uuid4().hex[:8]
    payload  = {
        "track_id": track_id or licence.track_id,
        "licensee_name": licence.licensee_name,
        "licensee_email": f"license_{uid}@email.com" or licence.licensee_email,
        "license_type": licence.licensee_type,
        "status": licence.status,
        "fee": licence.fee,
        "territory": licence.territory,
        "starts_at": licence.starts_at,
        "expires_at": licence.expires_at,
    }
    payload.update(overrides)

    return payload

def license_update_payload(**kwargs) -> dict:
    """Build a payload for PUT /licenses/<id> with only provided fields."""
    return {k: v for k, v in kwargs.items() if v is not None}