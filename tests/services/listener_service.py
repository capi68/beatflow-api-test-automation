"""Service layer for listener API interactions"""

import  requests
from tests.base.base_service import BaseService
from tests.utils.endpoints import ListenerEndpoints

class ListenerService(BaseService):
    """HTTP service for listener CRUD and authentication."""

    def list(self) -> requests.Response:
        """GET /listeners - list all listeners."""
        return self.get(ListenerEndpoints.BASE)

    def create(self, payload: dict) -> requests.Response:
        """POST /listeners - register a new listener."""
        return self.post(ListenerEndpoints.BASE, data=payload)

    def get_by_id(self, listener_id: int) -> requests.Response:
        """GET /listeners/<id> - get listener by id."""
        endpoint = ListenerEndpoints.DETAIL.format(listener_id=listener_id)
        return self.get(endpoint)

    def update(self, listener_id: int, payload: dict) -> requests.Response:
        """PUT /listeners/<id> - update listener fields."""
        endpoint = ListenerEndpoints.DETAIL.format(listener_id=listener_id)
        return self.put(endpoint, data=payload)

    def delete_listener(self, listener_id: int) -> requests.Response:
        """DELETE /listeners/<id> permanently delete listener."""
        endpoint = ListenerEndpoints.DETAIL.format(listener_id=listener_id)
        return self.delete(endpoint)

    def login(self, payload: dict) -> requests.Response:
        """POST /listeners/login - authenticate and get JWT token."""
        return self.post(ListenerEndpoints.LOGIN, data=payload)