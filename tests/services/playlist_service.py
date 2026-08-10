"""Service layer for playlist API interactions."""

import requests
from tests.base.base_service import BaseService
from tests.utils.endpoints import PlaylistEndpoints

class PlaylistService(BaseService):
    """HTTP service for playlist CRUD."""

    def list(self, listener_id: int = None, is_public: bool = None) -> requests.Response:
        """GET /playlists - list all playlist,
        optionally filterable by listener_id or is_public."""

        params = {}

        if listener_id is not None:
            params["listener_id"] = listener_id
        if is_public is not None:
            params["is_public"] = str(is_public).lower()

        return self.get(PlaylistEndpoints.BASE, params=params)

    def create(self, payload: dict) -> requests.Response:
        """POST /playlists - register a new playlist."""
        return self.post(PlaylistEndpoints.BASE, data=payload)

    def get_by_id(self, playlist_id: int) -> requests.Response:
        """GET /playlists/<id> - get playlist by id."""
        endpoint = PlaylistEndpoints.DETAIL.format(playlist_id=playlist_id)
        return self.get(endpoint)

    def update(self, playlist_id: int, payload: dict) -> requests.Response:
        """PUT /playlists/<id> - update playlists fields."""
        endpoint = PlaylistEndpoints.DETAIL.format(playlist_id=playlist_id)
        return self.put(endpoint, data=payload)

    def delete_playlist(self, playlist_id: int) -> requests.Response:
        """DELETE /playlists/<id> - permanently delete playlist."""
        endpoint = PlaylistEndpoints.DETAIL.format(playlist_id=playlist_id)
        return self.delete(endpoint)