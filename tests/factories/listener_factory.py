"""Factory for creating Listener preconditions.
Creates a listener via API and returns the response data.
Used when other entities (Subscriptions, playlist, stream) need a listener to exists first.
"""

from tests.services.listener_service import ListenerService
from tests.payloads.listener_payload import listener_create_payload
from tests.utils.constants import StatusCodes
from tests.utils.logger import get_logger

logger = get_logger(__name__)

class ListenerFactory:
    """Creates listener preconditions via API."""

    def __init__(self, service: ListenerService = None):
        self._service = service or ListenerService()

    def create(self, **overrides):
        """Create a listener and return the response.

        Args:
            **overrides: Any fields to overrides in the default payload.
        Returns:
            dict: The created listener response from the API.
        """
        payload = listener_create_payload(**overrides)


        response = self._service.create(payload)
        assert response.status_code == StatusCodes.CREATED, f"Factory failed to create listener: {response.text}"

        data = response.json()
        logger.info("Factory created listener id=%s, username=%s", data["id"], data["username"])

        return data

    def cleanup(self, listener_id: int):
        """DELETE listener created by the factory."""
        response = self._service.delete_listener(listener_id)

        if response.status_code == StatusCodes.OK:
            logger.info("Factory cleaned up listener id=%s", listener_id)
        else:
            logger.warning(
                "Factory cleanup failed for listener id=%s, (%s): %s",
                listener_id,
                response.status_code,
                response.text,
            )

