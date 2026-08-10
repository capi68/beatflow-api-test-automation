"""JSON Schemas for listener API response validations."""

LISTENER_RESPONSE_SCHEMA = {
    "type": "object",
    "required": ["id", "username", "email", "first_name", "last_name", "is_active", "created_at", "updated_at"],
    "properties": {
        "id": {"type": "integer"},
        "username": {"type": "string", "minLength": 3, "maxLength": 50},
        "first_name": {"type": "string"},
        "last_name": {"type": "string"},
        "email": {"type": "string", "format": "email"},
        "country": {"type": ["null", "string"]},
        "date_of_birth": {"type": ["null", "string"], "format": "date-time"},
        "is_active": {"type": "boolean"},
        "created_at": {"type": "string", "format": "date-time"},
        "updated_at": {"type": "string", "format": "date-time"},
    },
    "additionalProperties": False
}

LISTENER_LIST_SCHEMA = {
    "type": "array",
    "items": LISTENER_RESPONSE_SCHEMA
}

LISTENER_LOGIN_RESPONSE_SCHEMA = {
    "type": "object",
    "required": ["message", "token", "listener_id"],
    "properties": {
        "message": {"type": "string"},
        "token": {"type": "string"},
        "listener_id": {"type": "integer"},
    },
    "additionalProperties": False
}