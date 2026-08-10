"""Factory for creating Playlist preconditions.
Creates a playlist via API and returns the response data.
Used when others entities (playlist tracks) need a playlist to exist first.
"""

from tests.services.listener_service import ListenerService
from tests.services.playlist_service import PlaylistService
from tests.models.playlist_model import Playlist
from tests.payloads.playlist_payload import playlist_create_payload
from tests.factories.listener_factory import ListenerFactory
from tests.utils.constants import StatusCodes
from tests.utils.logger import get_logger

logger = get_logger(__name__)

class PlaylistFactory:
    """Creates playlist preconditions via API."""

    def __init__(self, listener_service: ListenerService, playlist_service: PlaylistService):
        self._playlist_service = playlist_service
        self._listener_factory = ListenerFactory(listener_service)

    def create(self, listener_id: int = None, **overrides) -> dict:
        """Create a playlist and return the response JSON.

        Args:
            listener_id: Existing listener ID. If None, a new listener is created automatically.

            **overrides: Any fields to overrides in the default payload.
        returns:
            dict: The created playlist response from the API.
        """
        #Create listener dependency if not provided
        if listener_id is None:
            listener = self._listener_factory.create()
            listener_id = listener["id"]

        #Create playlist
        playlist = Playlist(listener_id=listener_id)
        payload = playlist_create_payload(playlist, **overrides)


        response = self._playlist_service.create(payload)
        data = response.json()
        playlist_id = data["id"]

        assert response.status_code == StatusCodes.CREATED, f"Factory failed to create playlist: {response.text}"

        logger.info("Factory created playlist id=%s for listener_id=%s", playlist_id, listener_id)

        return data

    def cleanup(self, playlist_id) -> None:
        """DELETE playlist created by this factory."""
        response = self._playlist_service.delete_playlist(playlist_id)

        if response.status_code == StatusCodes.OK:
            logger.info("Factory cleaned up playlist id=%s", playlist_id)

        else:
            logger.warning(
                "Factory cleanup failed for playlist id=%s, (%s) = %s",
                playlist_id,
                response.status_code,
                response.text
            )

    def cleanup_all(self, listener_id: int) -> None:
        """DELETE all resources created by this factory"""
        self._listener_factory.cleanup(listener_id)
