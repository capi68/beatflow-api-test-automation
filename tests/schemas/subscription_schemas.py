"""JSON schemas for subscription API response validations."""

SUBSCRIPTION_RESPONSE_SCHEMA = {
    "type": "object",
    "required": ["id", "listener_id", "plan", "status", "started_at", "expires_at", "paused_at", "cancelled_at", "created_at", "updated_at"],
    "properties": {
        "id": {"type": "integer"},
        "listener_id": {"type": "integer"},
        "plan": {"type": "string", "enum": ["free", "basic", "premium"]},
        "status": {"type": "string", "enum": ["active", "paused", "cancelled", "expired"]},
        "started_at": {"type": "string", "format": "date-time"},
        "expires_at": {"type": ["null", "string"], "format": "date-time"},
        "paused_at": {"type": ["null", "string"], "format": "date-time"},
        "cancelled_at": {"type": ["null", "string"], "format": "date-time"},
        "created_at": {"type": "string", "format": "date-time"},
        "updated_at": {"type": "string", "format": "date-time"},
    },
    "additionalProperties": False,
}

SUBSCRIPTION_LIST_SCHEMA = {
    "type": "array",
    "items": SUBSCRIPTION_RESPONSE_SCHEMA
}