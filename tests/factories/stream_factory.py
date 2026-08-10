"""Factory for creating Streams preconditions.
Creates a stream via API and returns the response data.
"""
from tests.factories.subscription_factory import SubscriptionFactory
from tests.services.album_service import AlbumService
from tests.services.artist_service import ArtistService
from tests.services.listener_service import ListenerService
from tests.services.stream_service import StreamService
from tests.services.subscriptions_service import SubscriptionService
from tests.services.track_service import TrackService
from tests.factories.track_factory import TrackFactory
from tests.payloads.streams_payload import create_stream_payload
from tests.utils.constants import StatusCodes
from tests.utils.logger import get_logger

logger = get_logger(__name__)

class StreamFactory:
    """Creates preconditions via API."""

    def __init__(
            self,
            stream_service: StreamService,
            listener_service: ListenerService,
            artist_service: ArtistService,
            album_service: AlbumService,
            track_service: TrackService,
            subscription_service: SubscriptionService
    ):
        self._track_service = track_service
        self._stream_service = stream_service
        self._album_service = album_service
        self._track_factory = TrackFactory(artist_service, album_service, track_service)
        self._subscription_factory = SubscriptionFactory(subscription_service, listener_service)

    def create(self, track_id: int = None, listener_id: int = None, **overrides) -> dict:
        """Create a track and return the response JSON.

        Args:
            track_id: Existing track ID. If None, a new track is created automatically.
            listener_id: Existing listener ID. If None, a new listener is created automatically.
            **overrides: Any fields to overrides in the default payload.
        Returns:
            dict: The created track response from the API.
        """
        artist_id = None
        album_id = None
        subscription_id = None
        #Create track dependency if not provided
        if track_id is None:
            track = self._track_factory.create()
            track_id = track["id"]
            album_id = track["album_id"]
            artist_id = track["artist_id"]

        self._album_service.update(album_id, {"status": "published"})

        get_response = self._track_service.get_by_id(track_id)
        get_data = get_response.json()
        duration_seconds = get_data["duration_seconds"]

        #Create listener with active subscription via Factory
        if listener_id is None:
            listener_subscription = self._subscription_factory.create()
            subscription_id = listener_subscription["id"]
            listener_id = listener_subscription["listener_id"]

        #Create stream
        payload = create_stream_payload(listener_id=listener_id, track_id=track_id, duration_seconds=duration_seconds)
        response = self._stream_service.create(payload)
        data = response.json()
        if artist_id is not None:
            data["artist_id"] = artist_id
        if album_id is not None:
            data["album_id"] = album_id
        if subscription_id is not None:
            data["subscription_id"] = subscription_id


        assert response.status_code == StatusCodes.CREATED, f"Factory failed to create stream: {response.text}"

        return data

    def cleanup_all(self,track_id: int, album_id: int, artist_id: int, listener_id: int, subscription_id: int) -> None:
        """DELETE all resources created by this factory."""
        self._track_factory.cleanup(track_id)
        self._album_service.update(album_id, {"status": "archived"})
        self._track_factory.cleanup_all(album_id, artist_id)
        self._subscription_factory.cleanup(subscription_id)
        self._subscription_factory.cleanup_all(listener_id)