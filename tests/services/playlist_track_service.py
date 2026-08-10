"""Service layer for Playlist Track API interactions."""

import requests
from tests.base.base_service import BaseService
from tests.utils.endpoints import PlaylistTracksEndpoints

class PlaylistTrackService(BaseService):
    """HTTP service for playlist track CRUD."""

    def list(self, playlist_id: int = None, **overrides) -> requests.Response:
        """GET /playlist-tracks - list all tracks of a specified playlist, filterable by playlist_id."""

        params = {}
        if playlist_id is not None:
            params["playlist_id"] = playlist_id

        return self.get(PlaylistTracksEndpoints.BASE, params=params)

    def create(self, payload: dict) -> requests.Response:
        """POST /playlist-tracks - register a new playlist-track."""
        return self.post(PlaylistTracksEndpoints.BASE, data=payload)

    def get_by_id(self, playlist_track_id: int) -> requests.Response:
        """GET /playlist-tracks/<id> - get playlist track registration by ID."""
        endpoint =  PlaylistTracksEndpoints.DETAIL.format(playlist_track_id=playlist_track_id)
        return self.get(endpoint)

    def update(self, playlist_track_id: int, payload: dict) -> requests.Response:
        """PUT /playlist-tracks - update playlist-tracks fields."""
        endpoint = PlaylistTracksEndpoints.DETAIL.format(playlist_track_id=playlist_track_id)
        return self.put(endpoint, data=payload)

    def delete_playlist_track(self, playlist_track_id: int) -> requests.Response:
        """DELETE /playlist-tracks/<id> - delete playlist-track."""
        endpoint = PlaylistTracksEndpoints.DETAIL.format(playlist_track_id=playlist_track_id)
        return self.delete(endpoint)
