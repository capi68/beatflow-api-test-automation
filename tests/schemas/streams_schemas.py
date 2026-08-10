"""JSON Schemas for stream API response validations."""

STREAM_RESPONSE_SCHEMA = {
    "type": "object",
    "required": ["id", "listener_id", "track_id", "duration_seconds", "completed", "streamed_at"],
    "properties": {
        "id": {"type": "integer"},
        "listener_id": {"type": "integer"},
        "track_id": {"type": "integer"},
        "duration_seconds": {"type": "integer"},
        "completed": {"type": "boolean"},
        "streamed_at": {"type": "string", "format": "date-time"}
    },
    "additionalProperties": False,
}

STREAM_LIST_SCHEMA = {
    "type": "array",
    "items": STREAM_RESPONSE_SCHEMA
}