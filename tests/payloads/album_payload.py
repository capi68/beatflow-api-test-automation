"""Payload builders for album API requests."""

from tests.models.album_model import Album

def album_create_payload(album: Album = None, artist_id: int = None, **overrides) -> dict:
    """Build a valid payload for POST /albums."""

    if album is None:
        album = Album()
    payload = {
        "artist_id": artist_id or album.artist_id,
        "title": album.title,
        "description": album.description,
        "release_year": album.release_year,
        "genre_id": album.genre_id,
        "cover_url": album.cover_url,
    }
    payload.update(overrides)

    return payload

def album_update_payload(**kwargs) -> dict:
    """Build a payload for PUT /albums/<id> with only provide fields."""
    return {k: v for k, v in kwargs.items() if v is not None}