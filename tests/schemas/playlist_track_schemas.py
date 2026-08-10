"""JSON Schemas from Playlist tracks API response validations."""

PLAYLIST_TRACK_RESPONSE_SCHEMA = {
    "type": "object",
    "required": ["id", "playlist_id", "track_id", "position", "added_at"],
    "properties": {
        "id": {"type": "integer"},
        "playlist_id": {"type": "integer"},
        "track_id": {"type": "integer"},
        "position": {"type": "integer"},
        "added_at": {"type": "string", "format": "date-time"}
    },
    "additionalProperties": False,
}

PLAYLIST_TRACK_GET_RESPONSE_SCHEMA = {
    "type": "array",
    "items": {
        "type": "object",
        "required": ["id", "playlist_id", "track_id", "position", "added_at", "track_title", "duration_seconds", "album_id"],
        "properties": {
            "id": {"type": "integer"},
            "playlist_id": {"type": "integer"},
            "track_id": {"type": "integer"},
            "position": {"type": "integer"},
            "added_at": {"type": "string", "format": "date-time"},
            "track_title": {"type": "string"},
            "duration_seconds": {"type": "integer"},
            "album_id": {"type": "integer"},
            },
    },
}