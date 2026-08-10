"""Service layer for Tracks API interactions."""

import requests
from tests.base.base_service import BaseService
from tests.utils.endpoints import TracksEndpoints

class TrackService(BaseService):
    """HTTP service track CRUD and state management."""

    def list(self, album_id: int = None, genre_id: int = None, is_available: bool = None) -> requests.Response:
        """GET /tracks - list of tracks on an album, optionally filtered by album_id, genre_id, is_available."""

        params = {}

        if album_id is not None:
            params["album_id"] = album_id
        if genre_id is not None:
            params["genre_id"] = genre_id
        if is_available is not None:
            params["is_available"] = str(is_available).lower()

        return  self.get(TracksEndpoints.BASE, params=params)

    def create(self, payload: dict) -> requests.Response:
        """POST /tracks - register a new track."""
        return self.post(TracksEndpoints.BASE, data=payload)

    def get_by_id(self, track_id: int) -> requests.Response:
        """GET /tracks/<id> get track by id."""
        endpoint = TracksEndpoints.DETAIL.format(track_id=track_id)
        return self.get(endpoint)

    def update(self, track_id: int, payload: dict) -> requests.Response:
        """PUT /tracks/<id> - update data tracks fields."""
        endpoint = TracksEndpoints.DETAIL.format(track_id=track_id)
        return self.put(endpoint, data=payload)

    def delete_track(self, track_id: int) -> requests.Response:
        """DELETE /tracks/<id> - delete permanently a track by id."""
        endpoint = TracksEndpoints.DETAIL.format(track_id=track_id)
        return self.delete(endpoint)