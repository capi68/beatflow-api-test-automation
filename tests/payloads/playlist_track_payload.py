"""Payload builders from Playlist Track API requests."""

from tests.models.playlist_track_model import PlaylistTrack

def playlist_track_create_payload(playlist_track: PlaylistTrack = None, playlist_id: int = None, track_id: int = None, **overrides):
    """Build a valid payload for POST /playlist-tracks."""

    if playlist_track is None:
        playlist_track = PlaylistTrack()

    payload  = {
        "playlist_id": playlist_id or playlist_track.playlist_id,
        "track_id": track_id or playlist_track.track_id,
    }

    if playlist_track.position is not None:
        payload["position"] = playlist_track.position

    payload.update(overrides)
    return payload

def playlist_track_update_payload(**kwargs):
    """Build a payload for PUT /playlist-tracks/<id> with only provides fields."""
    return {k: v for k, v in kwargs.items() if v is not None}