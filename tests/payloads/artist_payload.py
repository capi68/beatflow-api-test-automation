"""Payload builders for artist API requests."""

import uuid
from tests.models.artist_model import Artist

def artist_create_payload(artist: Artist = None, **overrides) -> dict:
    """Build a valid payload for POST /artists."""
    if artist is None:
        artist = Artist()
    uid = uuid.uuid4().hex[:8]
    payload = {
        "stage_name": artist.stage_name,
        "first_name": artist.first_name,
        "last_name": artist.last_name,
        "email": artist.email or f"artist_{uid}@beatflow.com",
        "password": artist.password,
        "bio": artist.bio,
        "genre_id": artist.genre_id,
        "country": artist.country,
    }
    payload.update(overrides)
    return  payload

def artist_update_payload(**kwargs) -> dict:
    """Build a payload  for PUT /artists/<id> with only the provided fields."""
    return {k: v for k, v in kwargs.items() if v is not None}

def artist_login_payload(email: str, password: str) -> dict:
    """Build payload for POST /artists/login."""
    return {"email": email, "password": password}