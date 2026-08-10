"""JSON Schemas from Playlist API response validations."""

PLAYLIST_RESPONSE_SCHEMA = {
    "type": "object",
    "required": ["id", "listener_id", "name", "is_public", "track_count", "created_at", "updated_at"],
    "properties": {
        "id": {"type": "integer"},
        "listener_id": {"type": "integer"},
        "name": {"type": "string", "minLength": 1, "maxLength": 200},
        "description": {"type": ["null", "string"], "maxLength": 500},
        "is_public": {"type": "boolean"},
        "track_count": {"type": "integer"},
        "created_at": {"type": "string", "format": "date-time"},
        "updated_at": {"type": "string", "format": "date-time"},
    },
    "additionalProperties": False
}

PLAYLIST_LIST_SCHEMA = {
    "type": "array",
    "items": PLAYLIST_RESPONSE_SCHEMA
}