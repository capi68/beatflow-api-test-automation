"""Service layer for Royalty APY interactions."""

import requests
from tests.base.base_service import BaseService
from tests.utils.endpoints import RoyaltyEndpoints

class RoyaltyService(BaseService):
    """HTTP service royalty CRUD and state management."""

    def list(self, artist_id: int =  None, track_id: int = None, status: str = None) -> requests.Response:
        """GET /royalties - list all royalties, optionally filtered by artist_id, track_id and status."""

        params = {}

        if artist_id is not None:
            params["artist_id"] = artist_id
        if track_id is not None:
            params["track_id"] = track_id
        if status is not None:
            params["status"] = status
        return self.get(RoyaltyEndpoints.BASE, params=params)

    def create(self, payload: dict) -> requests.Response:
        """POST /royalties - register a new royalty."""
        return self.post(RoyaltyEndpoints.BASE, data=payload)

    def get_by_id(self, royalty_id: int) -> requests.Response:
        """GET /royalties/<id> - get royalty by id."""
        endpoint = RoyaltyEndpoints.DETAIL.format(royalty_id=royalty_id)
        return self.get(endpoint)

    def update(self, royalty_id: int, payload: dict) -> requests.Response:
        """PUT /royalties/<id> - update data royalty fields."""
        endpoint = RoyaltyEndpoints.DETAIL.format(royalty_id=royalty_id)
        return self.put(endpoint, data=payload)