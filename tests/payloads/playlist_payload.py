"""Payload builders from Playlist API requests."""

from tests.models.playlist_model import Playlist

def playlist_create_payload(playlist: Playlist = None, listener_id: int = None, **overrides) -> dict:
    """Build a valid payload for POST /playlists."""

    if playlist is None:
        playlist = Playlist()

    payload = {
        "listener_id": listener_id or playlist.listener_id,
        "name": playlist.name,
        "description": playlist.description,
        "is_public": playlist.is_public,
        "track_count": playlist.track_count
    }
    payload.update(overrides)

    return payload

def playlist_update_payload(**kwargs) -> dict:
    """Build a payload for PUT /playlist/<id> with only provides fields."""
    return {k: v for k, v in kwargs.items() if v is not  None}