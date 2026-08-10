"""Factory for creating Album preconditions.
Creates an album via API and returns the response data.
Used when others entities (tracks) need an Album to exist first.
"""

from tests.services.album_service import AlbumService
from tests.services.artist_service import ArtistService
from tests.models.album_model import Album
from tests.payloads.album_payload import album_create_payload
from tests.factories.artist_factory import ArtistFactory

from tests.utils.constants import StatusCodes
from tests.utils.logger import get_logger

logger = get_logger(__name__)

class AlbumFactory:
    """Creates album preconditions via API."""

    def __init__(self, artist_service: ArtistService, album_service: AlbumService):
        self._album_service = album_service
        self._artist_factory = ArtistFactory(artist_service)

    def create(self, artist_id: int = None, **overrides):
        """Create an album and return the response JSON.

        Args:
            artist_id: Existing artist ID. If None, a new artist is created automatically.

            **overrides: Any fields to overrides in the default payload.
        returns:
            dict: The created album response from the API.
        """
        #Create artist dependency if not provided
        if artist_id is None:
            artist = self._artist_factory.create()
            artist_id = artist["id"]

        album = Album(artist_id=artist_id)
        payload = album_create_payload(album, **overrides)

        response = self._album_service.create(payload)
        data = response.json()
        album_id = data["id"]

        assert response.status_code == StatusCodes.CREATED, f"Factory failed to create album: {response.text}"

        logger.info("Factory created album id=%s for artist_id=%s", album_id, artist_id)

        return data

    def cleanup(self, album_id) ->  None:
        """DELETE album created by this factory."""
        response = self._album_service.delete_album(album_id)

        if response.status_code == StatusCodes.OK:
            logger.info("Factory cleaned up album id=%s", album_id)
        else:
            logger.warning(
                "Factory cleanup failed for album id=%s, (%s): %s",
                album_id,
                response.status_code,
                response.text
            )


    def cleanup_all(self, artist_id: int) -> None:
        """DELETE all resources created by this factory"""
        self._artist_factory.cleanup(artist_id)