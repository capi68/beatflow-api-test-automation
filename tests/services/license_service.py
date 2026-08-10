"""Service layer for License API interactions."""

import requests
from tests.base.base_service import BaseService
from tests.utils.endpoints import LicenseEndpoints

class LicenseService(BaseService):
    """HTTP service license CRUD and state management."""

    def list(self, track_id: int = None, status: str = None, license_type: str = None) -> requests.Response:
        """GET /licenses - list of all licenses, optionally filtered by track_id, status or license_type"""

        params = {}

        if track_id is not None:
            params["track_id"] = track_id
        if status is not None:
            params["status"] = status
        if license_type is not None:
            params["license_type"] = license_type

        return self.get(LicenseEndpoints.BASE, params=params)

    def create(self, payload: dict) -> requests.Response:
        """POST /licenses - register a new license."""
        return self.post(LicenseEndpoints.BASE, data=payload)

    def get_by_id(self, license_id: int) -> requests.Response:
        """GET /licenses/<id> - get license by id."""
        endpoint = LicenseEndpoints.DETAIL.format(license_id=license_id)
        return self.get(endpoint)

    def update(self, license_id: int, payload: dict) -> requests.Response:
        """PUT /licenses/<id> - update data license fields."""
        endpoint = LicenseEndpoints.DETAIL.format(license_id=license_id)
        return self.put(endpoint, data=payload)