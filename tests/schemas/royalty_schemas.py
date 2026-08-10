"""JSON Schemas for royalty response validations."""

ROYALTY_RESPONSE_SCHEMA = {
    "type": "object",
    "required": ["id","artist_id","track_id","stream_count","amount","period_start","period_end","created_at","updated_at"],
    "properties": {
        "id": {"type": "integer"},
        "artist_id": {"type": "integer"},
        "track_id": {"type": "integer"},
        "stream_count": {"type": "integer"},
        "amount": {"type": "number", "minimum":0, "maximum": 1000000},
        "status": {"type": "string", "enum": ["pending","processing","paid","failed"]},
        "period_start": {"type": "string", "format": "date-time"},
        "period_end": {"type": "string", "format": "date-time"},
        "processed_at": {"type": ["null","string"], "format": "date-time"},
        "paid_at": {"type": ["null","string"], "format": "date-time"},
        "failed_at": {"type": ["null","string"], "format": "date-time"},
        "failure_reason": {"type": ["null","string"], "maxLength": 255},
        "created_at": {"type": "string", "format": "date-time"},
        "updated_at": {"type": "string", "format": "date-time"},
    },
    "additionalProperties": False,
}

ROYALTY_LIST_RESPONSE = {
    "type": "array",
    "items": ROYALTY_RESPONSE_SCHEMA
}