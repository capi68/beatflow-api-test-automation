"""Service layer for subscriptions API interactions."""

import  requests
from tests.base.base_service import BaseService
from  tests.utils.endpoints import SubscriptionEndpoints

class SubscriptionService(BaseService):
    """HTTP service for subscription CRUD."""

    def list(self, listener_id: int = None, status: str = None) -> requests.Response:
        """GET /subscriptions list all subscriptions,
        optionally filterable by listener_id or status"""

        params = {}
        if listener_id is not None:
            params["listener_id"] = listener_id
        if status is not None:
            params["status"] = status

        return self.get(SubscriptionEndpoints.BASE, params=params)

    def create(self, payload: dict) -> requests.Response:
        """POST /subscriptions - Register a new subscriptions."""
        return  self.post(SubscriptionEndpoints.BASE, data=payload)

    def get_by_id(self, subscription_id: int) -> requests.Response:
        """GET /subscriptions/<id> - get subscription by id."""
        endpoint = SubscriptionEndpoints.DETAIL.format(subscription_id=subscription_id)
        return self.get(endpoint)

    def update(self, subscription_id: int, payload: dict) -> requests.Response:
        """PUT /subscriptions/<id> - update subscriptions fields."""
        endpoint = SubscriptionEndpoints.DETAIL.format(subscription_id=subscription_id)
        return self.put(endpoint, data=payload)