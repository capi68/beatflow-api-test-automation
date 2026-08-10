"""JSON Schemas for artist API response validations."""

ARTIST_RESPONSE_SCHEMA = {
    "type": "object",
    "required": ["id", "stage_name", "first_name", "last_name", "email", "genre_id", "total_earnings", "is_active", "created_at", "updated_at"],
    "properties": {
        "id": {"type": "integer"},
        "stage_name": {"type": "string", "maxLength": 100},
        "first_name": {"type": "string"},
        "last_name": {"type": "string"},
        "email": {"type": "string", "format": "email"},
        "genre_id": {"type": ["null", "integer"]},
        "bio": {"type": ["null", "string"]},
        "country": {"type": ["null", "string"]},
        "total_earnings": {"type": "number", "minimum": 0.00},
        "is_active": {"type": "boolean"},
        "created_at": {"type": "string", "format": "date-time"},
        "updated_at": {"type": "string", "format": "date-time"},
    },
    "additionalProperties": False
}

ARTIST_LIST_SCHEMA = {
    "type": "array",
    "items": ARTIST_RESPONSE_SCHEMA,
}

ARTIST_LOGIN_RESPONSE_SCHEMA = {
    "type": "object",
    "required": ["message", "token", "artist_id"],
    "properties": {
        "message": {"type": "string"},
        "token": {"type": "string"},
        "artist_id": {"type": "integer"},
    },
    "additionalProperties": False
}