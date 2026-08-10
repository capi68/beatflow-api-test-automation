"""Payload builders from Track API requests."""

from tests.models.track_model import Track

def track_create_payload(track: Track = None, album_id: int = None, **overrides) -> dict:
    """Build a valid payload for POST /tracks."""

    if track is None:
        track = Track()

    payload = {
        "album_id": album_id or track.album_id,
        "title": track.title,
        "duration_seconds": track.duration_seconds,
        "track_number": track.track_number,
        "genre_id": track.genre_id,
        "is_available": track.is_available,
        "is_explicit": track.is_explicit,
    }
    payload.update(overrides)

    return payload

def track_update_payload(**kwargs) -> dict:
    """Build a payload  for PUT /tracks/<id> with only provides fields."""
    return {k: v for k, v in kwargs.items() if v is not None}