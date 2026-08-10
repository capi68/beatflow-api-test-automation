"""Factory for creating license preconditions.
Creates a license via API and returns the response data.
Used when others entities need a license to exist first.
"""

from tests.models.license_model import License
from tests.payloads.license_payloads import license_create_payload
from tests.factories.track_factory import TrackFactory
from tests.services.album_service import AlbumService
from tests.services.artist_service import ArtistService
from tests.services.license_service import LicenseService
from tests.services.track_service import TrackService
from tests.utils.constants import StatusCodes
from tests.utils.logger import get_logger

logger = get_logger(__name__)

class LicenseFactory:
    """Creates license preconditions via API"""
    def __init__(self, license_service: LicenseService, artist_service: ArtistService, album_service: AlbumService, track_service: TrackService):
        self._service = license_service
        self._track_factory = TrackFactory(artist_service, album_service, track_service)

    def create(self, track_id: int = None, **overrides) -> dict:
        """Create a license and return the response JSON.

        Args:
            track_id: Existing track ID. If None, a new track is created automatically.

            **overrides: Any fields to overrides in the default payload.
        returns:
            dict: The created playlist response from the API.
        """
        album_id = None
        artist_id = None
        #Create a track dependency if not provided
        if track_id is None:
            track = self._track_factory.create()
            track_id = track["id"]
            album_id = track["album_id"]
            artist_id = track["artist_id"]

        #Create license
        license = License(track_id=track_id)
        payload = license_create_payload(license, **overrides)
        response = self._service.create(payload)
        data = response.json()
        license_id = data["id"]

        if album_id is not None:
            data["album_id"] = album_id
        if artist_id is not None:
            data["artist_id"] = artist_id
        assert response.status_code == StatusCodes.CREATED, f"Factory failed to created license: {response.text}"
        logger.info("Factory created license id=%s for track_id=%s", license_id, track_id)
        return data

    def clean_up(self, license_id: int) -> None:
        """DELETE license created by this factory."""
        response = self._service.update(license_id, {"status": "revoked", "revocation_reason": "reason of revoked"})

        if response.status_code == StatusCodes.OK:
            logger.info("Factory revoked license id=%s", license_id)

        else:
            logger.warning(
                "Factory cleanup failed to revoked license id=%s, (%s) = %s",
                license_id,
                response.status_code,
                response.text
            )

    def cleanup_all(self, track_id: int, album_id: int, artist_id: int) -> None:
        """DELETE all resources created by this factory"""
        self._track_factory.cleanup(track_id)
        self._track_factory.cleanup_all(album_id, artist_id)