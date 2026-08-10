"""Factory for creating Track preconditions.
Creates a track via API and returns the response data.
Used when others entities (playlist_tracks) need a track to exist first.
"""

from tests.services.artist_service import ArtistService
from tests.services.album_service import AlbumService
from tests.services.track_service import TrackService
from tests.models.track_model import Track
from tests.payloads.track_payload import track_create_payload
from tests.factories.album_factory import AlbumFactory
from tests.payloads.album_payload import album_update_payload
from tests.utils.constants import StatusCodes
from tests.utils.logger import get_logger

logger = get_logger(__name__)

class TrackFactory:
    """Creates track preconditions via API."""

    def __init__(self, artist_service: ArtistService, album_service: AlbumService, track_service: TrackService):
        self._track_service = track_service
        self._album_factory = AlbumFactory(artist_service, album_service)

    def create(self, album_id: int = None, **overrides):
        """Create a track and return the response JSON.

        Args:
            album_id: Existing album ID. If None, a new album is created automatically.

            **overrides: Any fields to overrides in the default payload.
        Returns:
            dict: The created track response from the API.
        """

        artist_id = None
        #Create album dependency if not provided
        if album_id is None:
            album = self._album_factory.create()
            album_id = album["id"]
            artist_id = album["artist_id"]

        track = Track(album_id=album_id)
        payload = track_create_payload(track, **overrides)

        response = self._track_service.create(payload)
        data = response.json()
        track_id = data["id"]

        if artist_id is not None:
            data["artist_id"] = artist_id

        assert response.status_code == StatusCodes.CREATED, f"Factory failed to create track: {response.text}"

        logger.info("Factory created track id=%s for album_id=%s", track_id, album_id)

        return  data

    def cleanup(self, track_id: int) -> None:
        """DELETE track created by this factory."""
        response = self._track_service.delete_track(track_id)

        if response.status_code == StatusCodes.OK:
            logger.info("Factory cleaned up track id=%s", track_id)

        else:
            logger.warning(
                "Factory cleanup failed for track id=%s, (%s): %s",
                track_id,
                response.status_code,
                response.text
            )

    def cleanup_all(self, album_id: int, artist_id: int) -> None:
        """DELETE all resources created by this factory."""
        self._album_factory.cleanup(album_id)
        self._album_factory.cleanup_all(artist_id)
