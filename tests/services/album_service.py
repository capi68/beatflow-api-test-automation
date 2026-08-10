"""Service layer for Album API interactions."""

import requests
from tests.base.base_service import BaseService
from tests.utils.endpoints import AlbumEndpoints

class AlbumService(BaseService):
    """HTTP service album CRUD and state management."""

    def list(self, artist_id: int = None, status: str = None) -> requests.Response:
        """GET /albums - list all albums, optionally filtered by artist_id or status."""

        params = {}

        if artist_id is not None:
            params["artist_id"] = artist_id

        if status is not None:
            params["status"] = status

        return self.get(AlbumEndpoints.BASE, params=params)

    def create(self, payload: dict) -> requests.Response:
        """POST /albums - register a new album."""
        return self.post(AlbumEndpoints.BASE, data=payload)

    def get_by_id(self, album_id: int) -> requests.Response:
        """GET /albums/<id> - get album by id."""
        endpoint = AlbumEndpoints.DETAIL.format(album_id=album_id)
        return self.get(endpoint)

    def update(self, album_id: int, payload: dict) -> requests.Response:
        """PUT /albums/<id> - update data albums fields."""
        endpoint = AlbumEndpoints.DETAIL.format(album_id=album_id)
        return self.put(endpoint, data=payload)

    def delete_album(self, album_id: int) -> requests.Response:
        """DELETE /albums/<id> - delete permanently an album by id."""
        endpoint = AlbumEndpoints.DETAIL.format(album_id=album_id)
        return self.delete(endpoint)
