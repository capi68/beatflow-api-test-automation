"""Factory for creating Track preconditions.
Creates a track via API and returns the response data.
"""

from tests.services.album_service import AlbumService
from tests.services.artist_service import ArtistService
from tests.services.listener_service import ListenerService
from tests.services.track_service import TrackService
from tests.services.playlist_service import PlaylistService
from tests.services.playlist_track_service import PlaylistTrackService
from tests.payloads.playlist_track_payload import playlist_track_create_payload
from tests.factories.track_factory import TrackFactory
from tests.factories.playlist_factory import PlaylistFactory
from tests.utils.constants import StatusCodes
from tests.utils.logger import get_logger

logger = get_logger(__name__)

class PlaylistTrackFactory:
    """Creates preconditions via API."""

    def __init__(
            self,
            playlist_track_service: PlaylistTrackService,
            playlist_service: PlaylistService,
            listener_service: ListenerService,
            artist_service: ArtistService,
            album_service: AlbumService,
            track_service: TrackService
    ):
        self._playlist_track_service = playlist_track_service
        self._playlist_factory = PlaylistFactory(listener_service, playlist_service)
        self._track_factory = TrackFactory(artist_service, album_service, track_service)

    def create(self, track_id: int = None, playlist_id: int = None, **overrides) -> dict:
        """Create a track and return the response JSON.

        Args:
            track_id: Existing track ID. If None, a new track is created automatically.
            playlist_id: Existing playlist ID. If None, a new playlist is created automatically.
            **overrides: Any fields to overrides in the default payload.
        Returns:
            dict: The created track response from the API.
        """
        listener_id = None
        artist_id = None
        album_id = None
        #Create track dependency if not provided
        if track_id is None:
            track = self._track_factory.create()
            track_id = track["id"]
            album_id = track["album_id"]
            artist_id = track["artist_id"]

        #Create playlist dependency if not provided
        if playlist_id is None:
            playlist = self._playlist_factory.create()
            playlist_id = playlist["id"]
            listener_id = playlist["listener_id"]

        #Create playlist track
        payload = playlist_track_create_payload(track_id=track_id, playlist_id=playlist_id)
        response = self._playlist_track_service.create(payload)
        data = response.json()
        assert response.status_code == StatusCodes.CREATED, f"Factory failed to create playlist track: {response.text}"

        if listener_id is not None:
            data["listener_id"] = listener_id
        if artist_id is not None:
            data["artist_id"] = artist_id
        if album_id is not None:
            data["album_id"] = album_id

        return data

    def cleanup(self, playlist_track_id: int) -> None:
        """DELETE playlist track created by this factory."""
        response = self._playlist_track_service.delete_playlist_track(playlist_track_id)

        if response.status_code == StatusCodes.OK:
            logger.info("Factory cleaned up playlist_track id=%s", playlist_track_id)
        else:
            logger.warning(
                "Factory cleanup failed for playlist_track id=%s, (%s): %s",
                playlist_track_id,
                response.status_code,
                response.text
            )

    def cleanup_track_cascade(self,track_id: int, album_id: int, artist_id: int) -> None:
        """DELETE all track resources created by this factory."""
        self._track_factory.cleanup(track_id)
        self._track_factory.cleanup_all(album_id, artist_id)

    def cleanup_playlist_cascade(self,listener_id: int, playlist_id: int) -> None:
        """DELETE all playlist resources created by this factory."""
        self._playlist_factory.cleanup(playlist_id)
        self._playlist_factory.cleanup_all(listener_id)

    def cleanup_all(self,track_id: int, album_id: int, artist_id: int, listener_id: int, playlist_id: int) -> None:
        """DELETE all resources created by this factory."""
        self._track_factory.cleanup(track_id)
        self._track_factory.cleanup_all(album_id, artist_id)
        self._playlist_factory.cleanup(playlist_id)
        self._playlist_factory.cleanup_all(listener_id)