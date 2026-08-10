"""JSON Schemas for license API response validations."""

LICENSE_RESPONSE_SCHEMA = {
    "type": "object",
    "required": ["id","track_id","licensee_name","licensee_email","license_type","fee","created_at", "updated_at"],
    "properties": {
        "id": {"type": "integer"},
        "track_id": {"type": "integer"},
        "licensee_name": {"type": "string", "maxLength": 200},
        "licensee_email": {"type": "string", "format": "email"},
        "license_type": {"type": "string", "enum": ["sync", "mechanical", "performance", "master"]},
        "status": {"type": "string", "enum": ["requested", "approved", "revoked", "active", "expired"]},
        "fee": {"type": "integer", "minimum": 0, "maximum": 1000000},
        "territory": {"type": "string", "maxLength": 100},
        "starts_at":  {"type": ["null","string"], "format": "date-time"},
        "expires_at": {"type": ["null","string"], "format": "date-time"},
        "approved_at": {"type": ["null","string"], "format": "date-time"},
        "revoked_at": {"type": ["null","string"], "format": "date-time"},
        "revocation_reason": {"type": ["null", "string"], "maxLength": 255},
        "created_at": {"type": "string", "format": "date-time"},
        "updated_at": {"type": "string", "format": "date-time"},
    },
    "additionalProperties": False,
}

LICENSE_LIST_SCHEMA = {
    "type": "array",
    "items": LICENSE_RESPONSE_SCHEMA
}