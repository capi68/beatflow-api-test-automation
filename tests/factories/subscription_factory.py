"""Factory for creating Subscription preconditions.
Creates a subscriptions for a one listener via API and returns
the response data. Used when others entities (stream) need a listener with
active subscription to exist first.
"""

from tests.services.subscriptions_service import SubscriptionService
from tests.services.listener_service import ListenerService
from tests.factories.listener_factory import ListenerFactory
from tests.payloads.subscription_payload import subscription_create_payload, subscription_update_payload
from tests.models.subscription_model import Subscription

from tests.utils.constants import StatusCodes
from tests.utils.logger import get_logger

logger = get_logger(__name__)

class SubscriptionFactory:
    """Creates subscription preconditions via API."""

    def __init__(self, subscription_service: SubscriptionService, listener_service: ListenerService):
        self._subscription_service = subscription_service
        self._listener_factory = ListenerFactory(listener_service)

    def create(self, listener_id: int = None, **overrides):
        """Create a subscription and return the response JSON.

        Args:
            listener_id: Existing listener ID. If None, a new listener is created automatically.
            **overrides: Any fields to overrides in the default payload.
        returns:
            dict: The created album response from the API.
        """
        #Create listener dependency if not provided
        if listener_id is None:
            listener = self._listener_factory.create()
            listener_id = listener["id"]

        subscription = Subscription(listener_id=listener_id)
        payload = subscription_create_payload(subscription, **overrides)

        response = self._subscription_service.create(payload)
        data = response.json()

        assert  response.status_code == StatusCodes.CREATED, f"Factory failed to create subscription: {response.text}"
        return data

    def cleanup(self, subscription_id: int) -> None:
        """ DELETE subscription created by this factory."""
        clean_payload = subscription_update_payload(status="cancelled")
        response = self._subscription_service.update(subscription_id, clean_payload)

    def cleanup_all(self, listener_id: int) -> None:
        """DELETE all resources created by this factory"""
        self._listener_factory.cleanup(listener_id)