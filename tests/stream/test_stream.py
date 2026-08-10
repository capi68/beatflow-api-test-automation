"""Test for Stream API."""

import allure
import pytest

from tests.base.base_assertions import  BaseAssertions
from tests.factories.stream_factory import StreamFactory
from tests.payloads.streams_payload import create_stream_payload
from tests.payloads.track_payload import track_update_payload
from tests.schemas.streams_schemas import STREAM_RESPONSE_SCHEMA, STREAM_LIST_SCHEMA
from tests.factories.track_factory import TrackFactory
from tests.factories.subscription_factory import SubscriptionFactory
from tests.utils.constants import StatusCodes
from tests.utils.logger import get_logger

logger = get_logger(__name__)

@pytest.mark.stream
@allure.feature("Stream")
class TestStreamCreate(BaseAssertions):
    """Test for POST /streams - stream registration.

    Validates that the stream creation endpoint correctly handles.
    Valid input, missing fields valid data.
    """


    @allure.story("Create stream successfully")
    def test_create_stream_success(self, artist_service, album_service, track_service,subscription_service, listener_service, stream_service):
        """POST /streams - with valid required fields should return 201.
        and a response matching the Stream Response schema.
        """
        #Create track via factory
        track_factory = TrackFactory(artist_service, album_service, track_service)
        track = track_factory.create()
        track_id = track["id"]
        album_id = track["album_id"]
        artist_id = track["artist_id"]
        album_service.update(album_id, {"status": "published"})

        #Create listener with active subscription via Factory
        subscription_factory = SubscriptionFactory(subscription_service, listener_service)
        listener_subscription = subscription_factory.create()
        subscription_id = listener_subscription["id"]
        listener_id = listener_subscription["listener_id"]

        #Create stream
        service = stream_service
        payload = create_stream_payload(listener_id=listener_id, track_id=track_id)
        response = service.create(payload)

        self.using(response).assert_status_code_is(StatusCodes.CREATED)
        self.using(response).assert_response_has_key("id")
        self.using(response).assert_schema(STREAM_RESPONSE_SCHEMA)

        #CLEANUP
        track_factory.cleanup(track_id)
        album_service.update(album_id, {"status": "archived"})
        track_factory.cleanup_all(album_id, artist_id)
        subscription_factory.cleanup(subscription_id)
        subscription_factory.cleanup_all(listener_id)


    @allure.story("Create stream nonexistent listener")
    def test_create_stream_nonexistent_listener(self, artist_service, album_service, track_service,subscription_service, listener_service, stream_service):
        """POST /streams - with nonexistent listener should return 404.
        and message.
        """
        #Create track via factory
        track_factory = TrackFactory(artist_service, album_service, track_service)
        track = track_factory.create()
        track_id = track["id"]
        album_id = track["album_id"]
        artist_id = track["artist_id"]

        #Create stream
        service = stream_service
        payload = create_stream_payload(listener_id=999999, track_id=track_id)
        response = service.create(payload)

        self.using(response).assert_status_code_is(StatusCodes.NOT_FOUND)
        self.using(response).assert_response_has_key("message")

        #CLEANUP
        track_factory.cleanup(track_id)
        track_factory.cleanup_all(album_id, artist_id)


    @allure.story("Create stream nonexistent track_id")
    def test_create_stream_nonexistent_track(self, artist_service, album_service, track_service,subscription_service, listener_service, stream_service):
        """POST /streams - with nonexistent track_id should return 404.
        and message.
        """
        #Create listener with active subscription via Factory
        subscription_factory = SubscriptionFactory(subscription_service, listener_service)
        listener_subscription = subscription_factory.create()
        subscription_id = listener_subscription["id"]
        listener_id = listener_subscription["listener_id"]

        #Create stream
        service = stream_service
        payload = create_stream_payload(listener_id=listener_id, track_id=999999)
        response = service.create(payload)

        self.using(response).assert_status_code_is(StatusCodes.NOT_FOUND)
        self.using(response).assert_response_has_key("message")

        #CLEANUP
        subscription_factory.cleanup(subscription_id)
        subscription_factory.cleanup_all(listener_id)


    @allure.story("Create stream with not available track")
    def test_create_stream_unavailable_track(self, artist_service, album_service, track_service,subscription_service, listener_service, stream_service):
        """POST /streams - with is_available=False field should return 400.
        and message.
        """
        #Create track via factory and update to unavailable
        track_factory = TrackFactory(artist_service, album_service, track_service)
        track = track_factory.create()
        track_id = track["id"]
        album_id = track["album_id"]
        artist_id = track["artist_id"]
        update_payload = track_update_payload(is_available=False)
        update_track = track_service.update(track_id, update_payload)

        #Create listener with active subscription via Factory
        subscription_factory = SubscriptionFactory(subscription_service, listener_service)
        listener_subscription = subscription_factory.create()
        subscription_id = listener_subscription["id"]
        listener_id = listener_subscription["listener_id"]

        #Create stream
        service = stream_service
        payload = create_stream_payload(listener_id=listener_id, track_id=track_id)
        response = service.create(payload)

        self.using(response).assert_status_code_is(StatusCodes.BAD_REQUEST)
        self.using(response).assert_response_has_key("message")

        #CLEANUP
        track_factory.cleanup(track_id)
        track_factory.cleanup_all(album_id, artist_id)
        subscription_factory.cleanup(subscription_id)
        subscription_factory.cleanup_all(listener_id)


    @allure.story("Create stream with track in draft album")
    def test_create_stream_draft_album(self, artist_service, album_service, track_service,subscription_service, listener_service, stream_service):
        """POST /streams - with track in draft album should return 400.
        and message.
        """
        #Create track via factory and update to unavailable
        track_factory = TrackFactory(artist_service, album_service, track_service)
        track = track_factory.create()
        track_id = track["id"]
        album_id = track["album_id"]
        artist_id = track["artist_id"]

        #Create listener with active subscription via Factory
        subscription_factory = SubscriptionFactory(subscription_service, listener_service)
        listener_subscription = subscription_factory.create()
        subscription_id = listener_subscription["id"]
        listener_id = listener_subscription["listener_id"]

        #Create stream
        service = stream_service
        payload = create_stream_payload(listener_id=listener_id, track_id=track_id)
        response = service.create(payload)

        self.using(response).assert_status_code_is(StatusCodes.BAD_REQUEST)
        self.using(response).assert_response_has_key("message")

        #CLEANUP
        track_factory.cleanup(track_id)
        track_factory.cleanup_all(album_id, artist_id)
        subscription_factory.cleanup(subscription_id)
        subscription_factory.cleanup_all(listener_id)


    @allure.story("Create stream with listener with inactive subscription.")
    def test_listener_inactive_subscription(self, artist_service, album_service, track_service,subscription_service, listener_service, stream_service):
        """POST /streams - with listener with inactive subscription, should return 403
        and message."""
        #Create track via factory and update to unavailable
        track_factory = TrackFactory(artist_service, album_service, track_service)
        track = track_factory.create()
        track_id = track["id"]
        album_id = track["album_id"]
        artist_id = track["artist_id"]

        #Create listener with active subscription via Factory
        subscription_factory = SubscriptionFactory(subscription_service, listener_service)
        listener_subscription = subscription_factory.create()
        subscription_id = listener_subscription["id"]
        listener_id = listener_subscription["listener_id"]
        subscription_service.update(subscription_id, {"status": "paused"})
        #Create stream
        service = stream_service
        payload = create_stream_payload(listener_id=listener_id, track_id=track_id)
        response = service.create(payload)

        self.using(response).assert_status_code_is(StatusCodes.FORBIDDEN)
        self.using(response).assert_response_has_key("message")

        #CLEANUP
        track_factory.cleanup(track_id)
        track_factory.cleanup_all(album_id, artist_id)
        subscription_factory.cleanup(subscription_id)
        subscription_factory.cleanup_all(listener_id)


@pytest.mark.stream
@allure.feature("Streams")
class TestStreamRetrieval(BaseAssertions):
    """GET /streams - GET /streams/<id>."""

    @allure.story("Get streams list")
    def test_streams_list(self, stream_service):
        """GET /streams - should return 200 and a list of streams."""

        response = stream_service.list()
        data = response.json()
        logger.info("DATA: %s", data)

        self.using(response).assert_status_code_is(StatusCodes.OK)
        self.using(response).assert_schema(STREAM_LIST_SCHEMA)


    @allure.story("Get list filtered by listener_id")
    def test_get_list_by_listener_id(self, stream_service, artist_service, album_service, track_service, subscription_service, listener_service):
        """GET /streams?listener_id= - should return 200 and
        a list of streams for a specific listener"""
        #Create track via factory and update to unavailable
        track_factory = TrackFactory(artist_service, album_service, track_service)
        track = track_factory.create()
        track_id = track["id"]
        album_id = track["album_id"]
        artist_id = track["artist_id"]
        album_service.update(album_id, {"status": "published"})

        #Create listener with active subscription via Factory
        subscription_factory = SubscriptionFactory(subscription_service, listener_service)
        listener_subscription = subscription_factory.create()
        subscription_id = listener_subscription["id"]
        listener_id = listener_subscription["listener_id"]

        #Create stream
        service = stream_service
        payload = create_stream_payload(listener_id=listener_id, track_id=track_id)
        response = service.create(payload)

        #GET list by listener_id
        get_response = stream_service.list(listener_id)
        get_data = get_response.json()

        self.using(get_response).assert_status_code_is(StatusCodes.OK)
        assert all(streams["listener_id"] == listener_id for streams in get_data)

        #CLEANUP
        track_factory.cleanup(track_id)
        album_service.update(album_id, {"status": "archived"})
        track_factory.cleanup_all(album_id, artist_id)
        subscription_factory.cleanup(subscription_id)
        subscription_factory.cleanup_all(listener_id)


    @allure.story("Get list filtered by track_id")
    def test_get_list_by_track_id(self, stream_service, artist_service, album_service, track_service, subscription_service, listener_service):
        """GET /streams?track_id= - should return 200 and
        a list of streams for a specific track"""
        #Create track via factory and update to unavailable
        track_factory = TrackFactory(artist_service, album_service, track_service)
        track = track_factory.create()
        track_id = track["id"]
        album_id = track["album_id"]
        artist_id = track["artist_id"]
        album_service.update(album_id, {"status": "published"})

        #Create listener with active subscription via Factory
        subscription_factory = SubscriptionFactory(subscription_service, listener_service)
        listener_subscription = subscription_factory.create()
        subscription_id = listener_subscription["id"]
        listener_id = listener_subscription["listener_id"]

        #Create stream
        service = stream_service
        payload = create_stream_payload(listener_id=listener_id, track_id=track_id)
        response = service.create(payload)

        #GET list by listener_id
        get_response = stream_service.list(track_id=track_id)
        get_data = get_response.json()

        self.using(get_response).assert_status_code_is(StatusCodes.OK)
        assert all(streams["track_id"] == track_id for streams in get_data)

        #CLEANUP
        track_factory.cleanup(track_id)
        album_service.update(album_id, {"status": "archived"})
        track_factory.cleanup_all(album_id, artist_id)
        subscription_factory.cleanup(subscription_id)
        subscription_factory.cleanup_all(listener_id)


    @allure.story("Get stream by id")
    def test_get_by_id(self, stream_service, artist_service, album_service, track_service, subscription_service, listener_service):
        """GET /streams/<id> - should return 200 and
        a stream by ID."""
        #Create track via factory and update to unavailable
        track_factory = TrackFactory(artist_service, album_service, track_service)
        track = track_factory.create()
        track_id = track["id"]
        album_id = track["album_id"]
        artist_id = track["artist_id"]
        album_service.update(album_id, {"status": "published"})

        #Create listener with active subscription via Factory
        subscription_factory = SubscriptionFactory(subscription_service, listener_service)
        listener_subscription = subscription_factory.create()
        subscription_id = listener_subscription["id"]
        listener_id = listener_subscription["listener_id"]

        #Create stream
        service = stream_service
        payload = create_stream_payload(listener_id=listener_id, track_id=track_id)
        response = service.create(payload)

        #GET list by listener_id
        get_response = stream_service.get_by_id(response.json()["id"])

        self.using(get_response).assert_status_code_is(StatusCodes.OK)
        self.using(get_response).assert_response_has_key_value("id", response.json()["id"])

        #CLEANUP
        track_factory.cleanup(track_id)
        album_service.update(album_id, {"status": "archived"})
        track_factory.cleanup_all(album_id, artist_id)
        subscription_factory.cleanup(subscription_id)
        subscription_factory.cleanup_all(listener_id)


@pytest.mark.stream
@allure.feature("Streams")
class TestsSideEffectsStream(BaseAssertions):
    """Side effects Streams API Tests."""

    @allure.story("Create stream duration less than ten seconds")
    def test_create_stream_duration_less_than_ten_seconds(self, stream_service, artist_service, album_service, track_service, subscription_service, listener_service):
        """POST /streams - with duration_seconds < 10 should return 400
        and message."""
        #Create track via factory and update to unavailable
        track_factory = TrackFactory(artist_service, album_service, track_service)
        track = track_factory.create()
        track_id = track["id"]
        album_id = track["album_id"]
        artist_id = track["artist_id"]
        album_service.update(album_id, {"status": "published"})

        #Create listener with active subscription via Factory
        subscription_factory = SubscriptionFactory(subscription_service, listener_service)
        listener_subscription = subscription_factory.create()
        subscription_id = listener_subscription["id"]
        listener_id = listener_subscription["listener_id"]

        #Create stream
        service = stream_service
        payload = create_stream_payload(listener_id=listener_id, track_id=track_id, duration_seconds=9)
        response = service.create(payload)

        self.using(response).assert_status_code_is(StatusCodes.BAD_REQUEST)
        self.using(response).assert_response_has_key("message")

        #CLEANUP
        track_factory.cleanup(track_id)
        album_service.update(album_id, {"status": "archived"})
        track_factory.cleanup_all(album_id, artist_id)
        subscription_factory.cleanup(subscription_id)
        subscription_factory.cleanup_all(listener_id)


    @allure.story("Create stream duration_seconds exceed duration_seconds of a track")
    def test_create_stream_duration_seconds_exceeded(self, stream_service, artist_service, album_service, track_service, subscription_service, listener_service):
        """POST /streams - with duration_seconds > track duration_seconds, API should reject
        exceeded value, and keep track duration_seconds"""
        #Create track via factory and update to unavailable
        track_factory = TrackFactory(artist_service, album_service, track_service)
        track = track_factory.create()
        track_id = track["id"]
        album_id = track["album_id"]
        artist_id = track["artist_id"]
        exceeded_value = track["duration_seconds"] + 1
        album_service.update(album_id, {"status": "published"})

        #Create listener with active subscription via Factory
        subscription_factory = SubscriptionFactory(subscription_service, listener_service)
        listener_subscription = subscription_factory.create()
        subscription_id = listener_subscription["id"]
        listener_id = listener_subscription["listener_id"]

        #Create stream
        service = stream_service
        payload = create_stream_payload(listener_id=listener_id, track_id=track_id, duration_seconds=exceeded_value)
        response = service.create(payload)

        assert exceeded_value > track["duration_seconds"]
        self.using(response).assert_status_code_is(StatusCodes.CREATED)
        assert  response.json()["duration_seconds"] == track["duration_seconds"]

        #CLEANUP
        track_factory.cleanup(track_id)
        album_service.update(album_id, {"status": "archived"})
        track_factory.cleanup_all(album_id, artist_id)
        subscription_factory.cleanup(subscription_id)
        subscription_factory.cleanup_all(listener_id)


    @allure.story("Max streams per day subscription free")
    def test_max_daily_streams_subscription_free(self, stream_service, artist_service, album_service, track_service, subscription_service, listener_service):
        """POST /streams - free subscription max daily streams for track is 5."""
        #Create 5 streams via Factory
        factory = StreamFactory(stream_service, listener_service, artist_service, album_service, track_service, subscription_service)
        stream = factory.create()
        listener_id = stream["listener_id"]
        track_id = stream["track_id"]
        album_id = stream["album_id"]
        artist_id = stream["artist_id"]
        subscription_id = stream["subscription_id"]
        for i in range(4):
            factory.create(listener_id=listener_id, track_id=track_id)

        #create stream number 6
        payload = create_stream_payload(listener_id=listener_id, track_id=track_id)
        response = stream_service.create(payload)

        self.using(response).assert_status_code_is(StatusCodes.FORBIDDEN)
        self.using(response).assert_response_has_key("message")

        #CLEANUP
        factory.cleanup_all(track_id, album_id, artist_id, listener_id, subscription_id)


    @allure.story("Max streams per day subscription basic")
    def test_max_daily_streams_subscription_basic(self, stream_service, artist_service, album_service, track_service, subscription_service, listener_service):
        """POST /streams - basic subscription max daily streams for track is 50."""
        #Create 49 streams via Factory
        factory = StreamFactory(stream_service, listener_service, artist_service, album_service, track_service, subscription_service)
        stream = factory.create()
        listener_id = stream["listener_id"]
        track_id = stream["track_id"]
        album_id = stream["album_id"]
        artist_id = stream["artist_id"]
        subscription_id = stream["subscription_id"]
        subscription_service.update(subscription_id, {"plan": "basic"})
        for i in range(49):
            factory.create(listener_id=listener_id, track_id=track_id)

        #create stream number 51
        payload = create_stream_payload(listener_id=listener_id, track_id=track_id)
        response = stream_service.create(payload)

        self.using(response).assert_status_code_is(StatusCodes.FORBIDDEN)
        self.using(response).assert_response_has_key("message")

        #CLEANUP
        factory.cleanup_all(track_id, album_id, artist_id, listener_id, subscription_id)


    @allure.story("Max streams per day subscription unlimited")
    def test_max_daily_streams_subscription_premium(self, stream_service, artist_service, album_service, track_service, subscription_service, listener_service):
        """POST /streams - premium subscription max daily streams for track is unlimited."""
        #Create 99 streams via Factory
        factory = StreamFactory(stream_service, listener_service, artist_service, album_service, track_service, subscription_service)
        stream = factory.create()
        listener_id = stream["listener_id"]
        track_id = stream["track_id"]
        album_id = stream["album_id"]
        artist_id = stream["artist_id"]
        subscription_id = stream["subscription_id"]
        subscription_service.update(subscription_id, {"plan": "premium"})
        for i in range(99):
            factory.create(listener_id=listener_id, track_id=track_id)

        #create stream number 101
        payload = create_stream_payload(listener_id=listener_id, track_id=track_id)
        response = stream_service.create(payload)

        self.using(response).assert_status_code_is(StatusCodes.CREATED)

        #CLEANUP
        factory.cleanup_all(track_id, album_id, artist_id, listener_id, subscription_id)


    @allure.story("below 80% duration_seconds completed field is False")
    def test_create_stream_below_80_percent_marks_completed_false(self, stream_service, artist_service, album_service, track_service, subscription_service, listener_service):
        """POST /streams - below 80% duration_seconds completed field is false."""
        #Create track via factory
        track_factory = TrackFactory(artist_service, album_service, track_service)
        track = track_factory.create()
        track_id = track["id"]
        album_id = track["album_id"]
        artist_id = track["artist_id"]
        album_service.update(album_id, {"status": "published"})
        time_79 = int(track["duration_seconds"] * 0.79)

        #Create listener with active subscription via Factory
        subscription_factory = SubscriptionFactory(subscription_service, listener_service)
        listener_subscription = subscription_factory.create()
        subscription_id = listener_subscription["id"]
        listener_id = listener_subscription["listener_id"]

        #Create stream
        payload = create_stream_payload(listener_id=listener_id, track_id=track_id, duration_seconds=time_79)
        response = stream_service.create(payload)


        self.using(response).assert_response_has_key_value("completed", False)

        #CLEANUP
        track_factory.cleanup(track_id)
        album_service.update(album_id, {"status": "archived"})
        track_factory.cleanup_all(album_id, artist_id)
        subscription_factory.cleanup(subscription_id)
        subscription_factory.cleanup_all(listener_id)


    @allure.story("Over 80% duration_seconds completed field is True")
    def test_create_stream_over_80_percent_marks_completed_true(self, stream_service, artist_service, album_service, track_service, subscription_service, listener_service):
        """POST /streams - Over 80% duration_seconds completed field is True."""
        #Create track via factory
        track_factory = TrackFactory(artist_service, album_service, track_service)
        track = track_factory.create()
        track_id = track["id"]
        album_id = track["album_id"]
        artist_id = track["artist_id"]
        album_service.update(album_id, {"status": "published"})
        time_80 = int(track["duration_seconds"] * 0.80)

        #Create listener with active subscription via Factory
        subscription_factory = SubscriptionFactory(subscription_service, listener_service)
        listener_subscription = subscription_factory.create()
        subscription_id = listener_subscription["id"]
        listener_id = listener_subscription["listener_id"]

        #Create stream
        payload = create_stream_payload(listener_id=listener_id, track_id=track_id, duration_seconds=time_80)
        response = stream_service.create(payload)

        self.using(response).assert_response_has_key_value("completed", True)

        #CLEANUP
        track_factory.cleanup(track_id)
        album_service.update(album_id, {"status": "archived"})
        track_factory.cleanup_all(album_id, artist_id)
        subscription_factory.cleanup(subscription_id)
        subscription_factory.cleanup_all(listener_id)