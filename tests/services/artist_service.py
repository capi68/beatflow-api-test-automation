"""Service layer for artist API interactions."""

import requests
from tests.base.base_service import BaseService
from tests.utils.endpoints import ArtistEndpoints

class ArtistService(BaseService):
    """HTTP service for artist CRUD and authentication."""

    def list(self, genre_id: int = None) -> requests.Response:
        """GET /artists - list all artists, optionally filtered by genre_id."""
        if genre_id is None:
            return self.get(ArtistEndpoints.BASE)

        return self.get(ArtistEndpoints.BASE, params={"genre_id": genre_id})

    def create(self, payload: dict) -> requests.Response:
        """POST artists - register a new Artist."""
        return self.post(ArtistEndpoints.BASE, data=payload)

    def get_by_id(self, artist_id: int) -> requests.Response:
        """GET /artists/<id> - get artist by ID."""
        endpoint = ArtistEndpoints.DETAIL.format(artist_id=artist_id)
        return self.get(endpoint)

    def update(self, artist_id: int, payload: dict) -> requests.Response:
        """PUT /artists/<id> - update artist fields."""
        endpoint = ArtistEndpoints.DETAIL.format(artist_id=artist_id)
        return self.put(endpoint, data=payload)

    def delete_artist(self, artist_id: int) -> requests.Response:
        """DELETE /artists/<id> - permanently delete artist."""
        endpoint = ArtistEndpoints.DETAIL.format(artist_id=artist_id)
        return  self.delete(endpoint)

    def login(self, payload: dict) -> requests.Response:
        """POST /artists/login - authenticate and get JWT token."""
        return self.post(ArtistEndpoints.LOGIN, data=payload)
