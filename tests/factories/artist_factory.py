"""Factory for creating Artist preconditions.
Creates an artist via API and returns the response data.
Used when other entities (Albums, royalties) need an Artist to exist first.
"""

from tests.services.artist_service import ArtistService
from tests.payloads.artist_payload import artist_create_payload
from tests.utils.constants import StatusCodes
from tests.utils.logger import get_logger

logger = get_logger(__name__)

class ArtistFactory:
    """Creates artist preconditions via API."""

    def __init__(self, service: ArtistService = None):
        self._service = service or ArtistService()

    def create(self, **overrides):
        """Create an artist and return the response JSON.

        Args:
            **overrides: Any fields to overrides in the default payload
        Returns:
            dict: The created artist response from the API.
        """
        payload = artist_create_payload(**overrides)


        response = self._service.create(payload)
        assert response.status_code == StatusCodes.CREATED, f"Factory failed to create artist: {response.text}"

        data = response.json()
        logger.info("Factory created artist id=%s, stage_name=%s", data["id"], data["stage_name"])

        return data

    def cleanup(self, artist_id: int):
        """DELETE artist created by the factory"""
        response = self._service.delete_artist(artist_id)

        if response.status_code == StatusCodes.OK:
            logger.info("Factory cleaned up artist id=%s", artist_id)
        else:
            logger.warning(
                "Factory cleanup failed for artist id=%s, (%s): %s",
                artist_id,
                response.status_code,
                response.text,
            )