"""JSON Schemas for Track API response validations."""

TRACK_RESPONSE_SCHEMA = {
    "type": "object",
    "required": ["id", "album_id", "title", "duration_seconds", "track_number", "is_available",
            "is_explicit", "created_at", "updated_at"],
    "properties": {
        "id": {"type": "integer"},
        "album_id": {"type": "integer"},
        "title": {"type": "string", "maxLength": 200},
        "duration_seconds": {"type": "integer", "minimum": 30, "maximum": 3600},
        "track_number": {"type": "integer", "minimum": 1, "maximum": 50},
        "is_available": {"type": "boolean"},
        "is_explicit": {"type": "boolean"},
        "genre_id": {"type": ["null", "integer"]},
        "play_count": {"type": "integer", "minimum": 0},
        "created_at": {"type": "string", "format": "date-time"},
        "updated_at": {"type": "string", "format": "date-time"},
    },
    "additionalProperties":False,
}
TRACK_LIST_SCHEMA = {
    "type": "array",
    "items": TRACK_RESPONSE_SCHEMA
}