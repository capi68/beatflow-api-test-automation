"""JSON Schemas for Album API response validations."""

ALBUM_RESPONSE_SCHEMA = {
    "type": "object",
    "required": ["id", "artist_id", "title", "status", "created_at", "updated_at"],
    "properties": {
        "id": {"type": "integer"},
        "artist_id": {"type": "integer"},
        "title": {"type": "string", "maxLength": 200},
        "description": {"type": ["null", "string"], "maxLength": 500},
        "release_year": {"type": ["null", "integer"], "minimum": 1900, "maximum": 2100},
        "genre_id": {"type": ["null","integer"]},
        "status": {"type": "string", "enum": ["draft", "published", "archived"]},
        "cover_url": {"type": ["null", "string"]},
        "created_at": {"type": "string", "format": "date-time"},
        "updated_at": {"type": "string", "format": "date-time"},
    },
    "additionalProperties": False,
}

ALBUM_LIST_SCHEMA = {
    "type": "array",
    "items": ALBUM_RESPONSE_SCHEMA
}