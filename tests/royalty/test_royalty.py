"""Test for Royalty API."""

import allure
import pytest

from tests.base.base_assertions import BaseAssertions
from tests.conftest import royalty_service
from tests.models.royalty_model import Royalty
from tests.payloads.royalty_payload import create_royalty_payload, update_royalty_payload
from tests.factories.track_factory import TrackFactory
from tests.factories.stream_factory import StreamFactory
from tests.schemas.royalty_schemas import ROYALTY_RESPONSE_SCHEMA, ROYALTY_LIST_RESPONSE
from tests.utils.constants import StatusCodes
from tests.utils.logger import get_logger

logger = get_logger(__name__)

@pytest.mark.royalty
@allure.feature("Royalties")
class TestCreateRoyalty(BaseAssertions):
    """Test for POST /royalties - royalty registration.

    Validates that the royalty creation endpoint correctly handles
    valid input, missing fields valid data."""

    @allure.story("Create royalty successfully")
    def test_create_royalty_success(self, artist_service, album_service, track_service, royalty_service):
        """POST /royalties - with all valid required fields should return 201
        and a response matching the Royalty Response schema."""
        #Create track via factory
        factory = TrackFactory(artist_service, album_service, track_service)
        track = factory.create()
        track_id = track["id"]
        album_id = track["album_id"]
        artist_id = track["artist_id"]

        service = royalty_service
        royalty = Royalty(artist_id=artist_id, track_id=track_id)
        payload = create_royalty_payload(royalty)
        response = service.create(payload)
        data = response.json()

        self.using(response).assert_status_code_is(StatusCodes.CREATED)
        self.using(response).assert_schema(ROYALTY_RESPONSE_SCHEMA)
        self.using(response).assert_response_has_key("id")
        self.using(response).assert_response_has_key_value("track_id", payload["track_id"])

        #CLEANUP
        service.update(data["id"], {"status": "processing"})
        service.update(data["id"], {"status": "paid"})
        factory.cleanup(track_id)
        factory.cleanup_all(album_id, artist_id)


    @allure.story("Create royalty with nonexistent artist_id")
    def test_create_royalty_nonexistent_artist_id(self, artist_service, album_service, track_service, royalty_service):
        """POST /royalties - with nonexistent artis_id should return 404 and message."""
        #Create track via factory
        factory = TrackFactory(artist_service, album_service, track_service)
        track = factory.create()
        track_id = track["id"]
        album_id = track["album_id"]
        artist_id = track["artist_id"]

        service = royalty_service
        royalty = Royalty(artist_id=999999, track_id=track_id)
        payload = create_royalty_payload(royalty)
        response = service.create(payload)

        self.using(response).assert_status_code_is(StatusCodes.NOT_FOUND)
        self.using(response).assert_response_has_key("message")

        #CLEANUP
        factory.cleanup(track_id)
        factory.cleanup_all(album_id, artist_id)


    @allure.story("Create royalty with nonexistent track_id")
    def test_create_royalty_nonexistent_track_id(self, artist_service, album_service, track_service, royalty_service):
        """POST /royalties - with nonexistent track_id should return 404 and message."""
        #Create track via factory
        factory = TrackFactory(artist_service, album_service, track_service)
        track = factory.create()
        track_id = track["id"]
        album_id = track["album_id"]
        artist_id = track["artist_id"]

        service = royalty_service
        royalty = Royalty(artist_id=artist_id, track_id=999999)
        payload = create_royalty_payload(royalty)
        response = service.create(payload)

        self.using(response).assert_status_code_is(StatusCodes.NOT_FOUND)
        self.using(response).assert_response_has_key("message")

        #CLEANUP
        factory.cleanup(track_id)
        factory.cleanup_all(album_id, artist_id)


    @allure.story("Create royalty with track not owned by artist")
    def test_create_royalty_track_not_owned_by_artist(self, artist_service, album_service, track_service, royalty_service):
        """POST /royalties - with track not owned by artist should return 400 and message."""
        factory = TrackFactory(artist_service, album_service, track_service)
        #Create track 1 via factory
        track = factory.create()
        track_id = track["id"]
        album_id = track["album_id"]
        artist_id = track["artist_id"]

        #Create track 2 via factory
        track_2 = factory.create()
        track_id_2 = track_2["id"]
        album_id_2 = track_2["album_id"]
        artist_id_2 = track_2["artist_id"]

        service = royalty_service
        royalty = Royalty(artist_id=artist_id, track_id=track_id_2)
        payload = create_royalty_payload(royalty)
        response = service.create(payload)
        data = response.json()

        self.using(response).assert_status_code_is(StatusCodes.BAD_REQUEST)
        self.using(response).assert_response_has_key("message")

        #CLEANUP
        factory.cleanup(track_id)
        factory.cleanup(track_id_2)
        factory.cleanup_all(album_id, artist_id)
        factory.cleanup_all(album_id_2, artist_id_2)


    @allure.story("Create royalty with stream_count negative value")
    def test_create_royalty_stream_count_negative(self, artist_service, album_service, track_service, royalty_service):
        """POST /royalties - with stream_count negative value should return 400 and message."""
        factory = TrackFactory(artist_service, album_service, track_service)
        #Create track  via factory
        track = factory.create()
        track_id = track["id"]
        album_id = track["album_id"]
        artist_id = track["artist_id"]

        service = royalty_service
        royalty = Royalty(artist_id=artist_id, track_id=track_id)
        payload = create_royalty_payload(royalty, stream_count=-1)
        response = service.create(payload)

        self.using(response).assert_status_code_is(StatusCodes.BAD_REQUEST)
        self.using(response).assert_response_has_key("message")

        #CLEANUP
        factory.cleanup(track_id)
        factory.cleanup_all(album_id, artist_id)


    @allure.story("Create royalty with amount boundary value")
    @pytest.mark.parametrize("value", [-1, 1000001])
    def test_create_royalty_amount_boundary_value(self, artist_service, album_service, track_service, royalty_service, value):
        """POST /royalties - with amount boundary value should return 400 and message."""
        factory = TrackFactory(artist_service, album_service, track_service)
        #Create track  via factory
        track = factory.create()
        track_id = track["id"]
        album_id = track["album_id"]
        artist_id = track["artist_id"]

        service = royalty_service
        royalty = Royalty(artist_id=artist_id, track_id=track_id)
        payload = create_royalty_payload(royalty, amount=value)
        response = service.create(payload)

        self.using(response).assert_status_code_is(StatusCodes.BAD_REQUEST)
        self.using(response).assert_response_has_key("message")

        #CLEANUP
        factory.cleanup(track_id)
        factory.cleanup_all(album_id, artist_id)


    @allure.story("Create royalty period_start with invalid format")
    def test_create_royalty_period_start_invalid_format(self, artist_service, album_service, track_service, royalty_service):
        """POST /royalties - with period_start with invalid format should return 400 and message."""
        factory = TrackFactory(artist_service, album_service, track_service)
        #Create track  via factory
        track = factory.create()
        track_id = track["id"]
        album_id = track["album_id"]
        artist_id = track["artist_id"]

        service = royalty_service
        royalty = Royalty(artist_id=artist_id, track_id=track_id)
        payload = create_royalty_payload(royalty, period_start="15-01-2026")
        response = service.create(payload)

        self.using(response).assert_status_code_is(StatusCodes.BAD_REQUEST)
        self.using(response).assert_response_has_key("message")

        #CLEANUP
        factory.cleanup(track_id)
        factory.cleanup_all(album_id, artist_id)


    @allure.story("Create royalty period_end with invalid format")
    def test_create_royalty_period_end_invalid_format(self, artist_service, album_service, track_service, royalty_service):
        """POST /royalties - with period_end with invalid format should return 400 and message."""
        factory = TrackFactory(artist_service, album_service, track_service)
        #Create track  via factory
        track = factory.create()
        track_id = track["id"]
        album_id = track["album_id"]
        artist_id = track["artist_id"]

        service = royalty_service
        royalty = Royalty(artist_id=artist_id, track_id=track_id)
        payload = create_royalty_payload(royalty, period_end="15-01-2026")
        response = service.create(payload)

        self.using(response).assert_status_code_is(StatusCodes.BAD_REQUEST)
        self.using(response).assert_response_has_key("message")

        #CLEANUP
        factory.cleanup(track_id)
        factory.cleanup_all(album_id, artist_id)


    @allure.story("Create royalty with period_end before period_start")
    def test_create_royalty_period_end_before_period_start(self, artist_service, album_service, track_service, royalty_service):
        """POST /royalties - with period_end before period_start should return 400 and message."""
        factory = TrackFactory(artist_service, album_service, track_service)
        #Create track  via factory
        track = factory.create()
        track_id = track["id"]
        album_id = track["album_id"]
        artist_id = track["artist_id"]

        service = royalty_service
        royalty = Royalty(artist_id=artist_id, track_id=track_id)
        payload = create_royalty_payload(royalty, period_start="2026-02-15", period_end="2026-01-15")
        response = service.create(payload)

        self.using(response).assert_status_code_is(StatusCodes.BAD_REQUEST)
        self.using(response).assert_response_has_key("message")

        #CLEANUP
        factory.cleanup(track_id)
        factory.cleanup_all(album_id, artist_id)


    @allure.story("Create duplicated royalty per track and period")
    def test_create_duplicate_royalty_per_track_and_period(self, artist_service, album_service, track_service, royalty_service):
        """POST /royalties - duplicated royalty per track and period should return 409 and message."""
        factory = TrackFactory(artist_service, album_service, track_service)
        #Create track  via factory
        track = factory.create()
        track_id = track["id"]
        album_id = track["album_id"]
        artist_id = track["artist_id"]

        service = royalty_service
        #first royalty
        royalty = Royalty(artist_id=artist_id, track_id=track_id)
        payload = create_royalty_payload(royalty)
        response = service.create(payload)

        #second royalty
        response_2 = service.create(payload)

        self.using(response_2).assert_status_code_is(StatusCodes.CONFLICT)
        self.using(response_2).assert_response_has_key("message")

        #CLEANUP
        factory.cleanup(track_id)
        factory.cleanup_all(album_id, artist_id)


    @allure.story("Create royalty over maxLength failure_reason field")
    def test_create_royalty_maxlength_failure_reason(self, artist_service, album_service, track_service, royalty_service):
        """POST /royalties - over maxLength failure_reason field should return 400 and message."""
        factory = TrackFactory(artist_service, album_service, track_service)
        #Create track  via factory
        track = factory.create()
        track_id = track["id"]
        album_id = track["album_id"]
        artist_id = track["artist_id"]

        service = royalty_service
        royalty = Royalty(artist_id=artist_id, track_id=track_id)
        payload = create_royalty_payload(royalty)
        response = service.create(payload)
        data = response.json()

        update_payload = update_royalty_payload(status="failed", failure_reason="a" * 256)
        update_response = service.update(data["id"], update_payload)

        self.using(update_response).assert_status_code_is(StatusCodes.BAD_REQUEST)
        self.using(update_response).assert_response_has_key("message")

        #CLEANUP
        service.update(data["id"], {"status": "processing"})
        service.update(data["id"], {"status": "paid"})
        factory.cleanup(track_id)
        factory.cleanup_all(album_id, artist_id)


@pytest.mark.royalty
@allure.feature("Royalties")
class TestRoyaltyRetrieval(BaseAssertions):
    """Test GET /royalties - GET /royalties/i<d>"""


    @allure.story("Get royalties list.")
    def test_list_royalties(self, royalty_service):
        """GET /royalties - should return 200 and list of royalties."""

        response = royalty_service.list()

        self.using(response).assert_status_code_is(StatusCodes.OK)
        self.using(response).assert_schema(ROYALTY_LIST_RESPONSE)


    @allure.story("Get list filtered by artist_id")
    def test_list_filtered_by_artist_id(self, royalty_service, artist_service, album_service, track_service):
        """GET /royalties?artist_id=, should return 200 and
        a list of royalties filtered by artist_id"""
        factory = TrackFactory(artist_service, album_service, track_service)
        #Create track  via factory
        track = factory.create()
        track_id = track["id"]
        album_id = track["album_id"]
        artist_id = track["artist_id"]

        service = royalty_service
        royalty = Royalty(artist_id=artist_id, track_id=track_id)
        payload = create_royalty_payload(royalty)
        response = service.create(payload)
        data = response.json()

        #get list filtered by artist_id
        get_response = service.list(artist_id)
        get_data = get_response.json()

        self.using(get_response).assert_status_code_is(StatusCodes.OK)
        assert all(royalties["artist_id"] == artist_id for royalties in get_data)

        #CLEANUP
        service.update(data["id"], {"status": "processing"})
        service.update(data["id"], {"status": "paid"})
        factory.cleanup(track_id)
        factory.cleanup_all(album_id, artist_id)


    @allure.story("Get list filtered by track_id")
    def test_list_filtered_by_track_id(self, royalty_service, artist_service, album_service, track_service):
        """GET /royalties?track_id=, should return 200 and
        a list of royalties filtered by artist_id"""
        factory = TrackFactory(artist_service, album_service, track_service)
        #Create track  via factory
        track = factory.create()
        track_id = track["id"]
        album_id = track["album_id"]
        artist_id = track["artist_id"]

        service = royalty_service
        royalty = Royalty(artist_id=artist_id, track_id=track_id)
        payload = create_royalty_payload(royalty)
        response = service.create(payload)
        data = response.json()

        #get list filtered by artist_id
        get_response = service.list(track_id)
        get_data = get_response.json()

        self.using(get_response).assert_status_code_is(StatusCodes.OK)
        assert all(royalties["track_id"] == track_id for royalties in get_data)

        #CLEANUP
        service.update(data["id"], {"status": "processing"})
        service.update(data["id"], {"status": "paid"})
        factory.cleanup(track_id)
        factory.cleanup_all(album_id, artist_id)


    @allure.story("Get list filtered by status")
    def test_list_filtered_by_status(self, royalty_service, artist_service, album_service, track_service):
        """GET /royalties?status=, should return 200 and
        a list of royalties filtered by artist_id"""
        factory = TrackFactory(artist_service, album_service, track_service)
        #Create track  via factory
        track = factory.create()
        track_id = track["id"]
        album_id = track["album_id"]
        artist_id = track["artist_id"]

        service = royalty_service
        royalty = Royalty(artist_id=artist_id, track_id=track_id)
        payload = create_royalty_payload(royalty)
        response = service.create(payload)
        data = response.json()

        update_response = royalty_service.update(data["id"], {"status": "processing"})
        #get list filtered by artist_id
        get_response = service.list(status="processing")
        get_data = get_response.json()

        self.using(get_response).assert_status_code_is(StatusCodes.OK)
        assert all(royalties["status"] == "processing" for royalties in get_data)

        #CLEANUP
        service.update(data["id"], {"status": "paid"})
        factory.cleanup(track_id)
        factory.cleanup_all(album_id, artist_id)


    @allure.story("Get royalty by id.")
    def test_get_by_id(self, royalty_service, artist_service, album_service, track_service):
        """GET /royalties/<id>, should return 200 and a royalty by id."""
        factory = TrackFactory(artist_service, album_service, track_service)
        #Create track  via factory
        track = factory.create()
        track_id = track["id"]
        album_id = track["album_id"]
        artist_id = track["artist_id"]

        service = royalty_service
        royalty = Royalty(artist_id=artist_id, track_id=track_id)
        payload = create_royalty_payload(royalty)
        response = service.create(payload)
        data = response.json()

        #get by id.
        get_response = service.get_by_id(data["id"])
        get_data = get_response.json()

        self.using(get_response).assert_status_code_is(StatusCodes.OK)
        self.using(get_response).assert_response_has_key_value("id", data["id"])

        #CLEANUP
        service.update(data["id"], {"status": "processing"})
        service.update(data["id"], {"status": "paid"})
        factory.cleanup(track_id)
        factory.cleanup_all(album_id, artist_id)


    @allure.story("Get nonexistent royalty.")
    def test_get_nonexistent_royalty(self, royalty_service):
        """GET /royalties/999999, should return 404 and a message."""

        response = royalty_service.get_by_id(999999)

        self.using(response).assert_status_code_is(StatusCodes.NOT_FOUND)
        self.using(response).assert_response_has_key("message")


@pytest.mark.royalty
@allure.feature("Royalties")
class TestRoyaltyUpdate(BaseAssertions):
    """Test for PUT /royalties."""

    @allure.story("UPDATE royalties only permitted fields.")
    def test_update_permitted_fields(self, royalty_service, artist_service, album_service, track_service):
        """PUT /royalties/<id> - UPDATE royalties only permitted fields should return 200
        remains fields should persist."""
        factory = TrackFactory(artist_service, album_service, track_service)
        #Create track  via factory
        track = factory.create()
        track_id = track["id"]
        album_id = track["album_id"]
        artist_id = track["artist_id"]

        service = royalty_service
        royalty = Royalty(artist_id=artist_id, track_id=track_id)
        payload = create_royalty_payload(royalty)
        response = service.create(payload)
        data = response.json()

        #Update status and failure_reason
        update_response = service.update(data["id"], {"status": "failed", "failure_reason": "failure reason"})
        update_data = update_response.json()

        self.using(update_response).assert_status_code_is(StatusCodes.OK)
        self.using(update_response).assert_response_has_key_value("status", "failed")
        self.using(update_response).assert_response_has_key_value("failure_reason", "failure reason")
        self.using(update_response).assert_response_has_key_value("stream_count", data["stream_count"])

        #CLEANUP
        service.update(data["id"], {"status": "pending"})
        service.update(data["id"], {"status": "processing"})
        service.update(data["id"], {"status": "paid"})
        factory.cleanup(track_id)
        factory.cleanup_all(album_id, artist_id)


@pytest.mark.royalty
@allure.feature("Royalties")
class TestStatusMachine(BaseAssertions):
    """Test for Status machine /royalties/<id>."""

    @allure.story("Status machine starting in pending.")
    @pytest.mark.parametrize("value", ["processing", "failed"])
    def test_update_status_machine_starting_pending(self, royalty_service, artist_service, album_service, track_service, value):
        """only valid transition 'pending' > processing/failed.
        status 'processing' sets processed_at = NOW()
        status 'failed' sets failed_at = NOW()."""
        factory = TrackFactory(artist_service, album_service, track_service)
        #Create track  via factory
        track = factory.create()
        track_id = track["id"]
        album_id = track["album_id"]
        artist_id = track["artist_id"]

        service = royalty_service
        royalty = Royalty(artist_id=artist_id, track_id=track_id)
        payload = create_royalty_payload(royalty)
        response = service.create(payload)
        data = response.json()

        #update status.
        status_payload = update_royalty_payload(status=value)
        if value == "failed":
            status_payload["failure_reason"] = "Failure reason"
        status_response = service.update(data["id"], status_payload)
        status_data = status_response.json()

        self.using(status_response).assert_status_code_is(StatusCodes.OK)
        self.using(status_response).assert_response_has_key_value("id", data["id"])
        if status_data["status"] == "processing":
            assert status_data["processed_at"] is not None
        if status_data["status"] == "failed":
            assert status_data["failed_at"] is not None

        #CLEANUP
        if status_data["status"] == "processing":
            service.update(data["id"], {"status": "paid"})
        if status_data["status"] == "failed":
            service.update(data["id"], {"status": "pending"})
            service.update(data["id"], {"status": "processing"})
            service.update(data["id"], {"status": "paid"})

        factory.cleanup(track_id)
        factory.cleanup_all(album_id, artist_id)

    @allure.story("invalid update status machine starting in pending.")
    def test_invalid_update_status_machine_starting_pending(self, royalty_service, artist_service, album_service, track_service):
        """only valid transition 'pending' > processing/failed"""
        factory = TrackFactory(artist_service, album_service, track_service)
        #Create track  via factory
        track = factory.create()
        track_id = track["id"]
        album_id = track["album_id"]
        artist_id = track["artist_id"]

        service = royalty_service
        royalty = Royalty(artist_id=artist_id, track_id=track_id)
        payload = create_royalty_payload(royalty)
        response = service.create(payload)
        data = response.json()

        #update status.
        status_payload = update_royalty_payload(status="paid")
        status_response = service.update(data["id"], status_payload)

        self.using(status_response).assert_status_code_is(StatusCodes.BAD_REQUEST)
        self.using(status_response).assert_response_has_key("message")

        #CLEANUP
        service.update(data["id"], {"status": "processing"})
        service.update(data["id"], {"status": "paid"})
        factory.cleanup(track_id)
        factory.cleanup_all(album_id, artist_id)


    @allure.story("Status machine starting in processing.")
    @pytest.mark.parametrize("value", ["paid", "failed"])
    def test_update_status_machine_starting_processing(self, royalty_service, artist_service, album_service, track_service, value):
        """only valid transition 'processing' > paid/failed
        status 'paid' sets paid_at = NOW()"""
        factory = TrackFactory(artist_service, album_service, track_service)
        #Create track  via factory
        track = factory.create()
        track_id = track["id"]
        album_id = track["album_id"]
        artist_id = track["artist_id"]

        service = royalty_service
        royalty = Royalty(artist_id=artist_id, track_id=track_id)
        payload = create_royalty_payload(royalty)
        response = service.create(payload)
        data = response.json()

        service.update(data["id"], {"status": "processing"})

        #update status.
        status_payload = update_royalty_payload(status=value)
        if value == "failed":
            status_payload["failure_reason"] = "Failure reason"
        status_response = service.update(data["id"], status_payload)
        status_data = status_response.json()

        self.using(status_response).assert_status_code_is(StatusCodes.OK)
        self.using(status_response).assert_response_has_key_value("id", data["id"])
        if status_data["status"] == "paid":
            assert status_data["paid_at"] is not None

        #CLEANUP
        if status_data["status"] == "failed":
            service.update(data["id"], {"status": "pending"})
            service.update(data["id"], {"status": "processing"})
            service.update(data["id"], {"status": "paid"})

        factory.cleanup(track_id)
        factory.cleanup_all(album_id, artist_id)


    @allure.story("invalid update status machine starting in processing.")
    def test_invalid_update_status_machine_starting_processing(self, royalty_service, artist_service, album_service, track_service):
        """only valid transition 'pending' > paid/failed"""
        factory = TrackFactory(artist_service, album_service, track_service)
        #Create track  via factory
        track = factory.create()
        track_id = track["id"]
        album_id = track["album_id"]
        artist_id = track["artist_id"]

        service = royalty_service
        royalty = Royalty(artist_id=artist_id, track_id=track_id)
        payload = create_royalty_payload(royalty)
        response = service.create(payload)
        data = response.json()

        service.update(data["id"], {"status": "processing"})

        #update status.
        status_payload = update_royalty_payload(status="pending")
        status_response = service.update(data["id"], status_payload)

        self.using(status_response).assert_status_code_is(StatusCodes.BAD_REQUEST)
        self.using(status_response).assert_response_has_key("message")

        #CLEANUP
        service.update(data["id"], {"status": "paid"})
        factory.cleanup(track_id)
        factory.cleanup_all(album_id, artist_id)


    @allure.story("Status machine starting in failed.")
    def test_update_status_machine_starting_failed(self, royalty_service, artist_service, album_service, track_service):
        """only valid transition 'failed' > pending
        status 'pending' clears failed_at and failure_reason (retry)"""
        factory = TrackFactory(artist_service, album_service, track_service)
        #Create track  via factory
        track = factory.create()
        track_id = track["id"]
        album_id = track["album_id"]
        artist_id = track["artist_id"]

        service = royalty_service
        royalty = Royalty(artist_id=artist_id, track_id=track_id)
        payload = create_royalty_payload(royalty)
        response = service.create(payload)
        data = response.json()

        service.update(data["id"], {"status": "failed", "failure_reason": "Failure reason"})

        #update status.
        status_response = service.update(data["id"], {"status": "pending"})
        status_data = status_response.json()
        logger.info("STATUS: %s", status_data)

        self.using(status_response).assert_status_code_is(StatusCodes.OK)
        self.using(status_response).assert_response_has_key_value("id", data["id"])
        self.using(status_response).assert_response_has_key_value("failure_reason", None)
        self.using(status_response).assert_response_has_key_value("failed_at", None)

        #CLEANUP
        service.update(data["id"], {"status": "processing"})
        service.update(data["id"], {"status": "paid"})

        factory.cleanup(track_id)
        factory.cleanup_all(album_id, artist_id)


    @allure.story("invalid update status machine starting in failed.")
    @pytest.mark.parametrize("value", ["processing", "paid"])
    def test_invalid_update_status_machine_starting_failed(self, royalty_service, artist_service, album_service, track_service, value):
        """only valid transition 'failed' > pending"""
        factory = TrackFactory(artist_service, album_service, track_service)
        #Create track  via factory
        track = factory.create()
        track_id = track["id"]
        album_id = track["album_id"]
        artist_id = track["artist_id"]

        service = royalty_service
        royalty = Royalty(artist_id=artist_id, track_id=track_id)
        payload = create_royalty_payload(royalty)
        response = service.create(payload)
        data = response.json()

        service.update(data["id"], {"status": "failed", "failure_reason": "Failure reason"})

        #update status.
        status_payload = update_royalty_payload(status=value)
        status_response = service.update(data["id"], status_payload)

        self.using(status_response).assert_status_code_is(StatusCodes.BAD_REQUEST)
        self.using(status_response).assert_response_has_key("message")

        #CLEANUP
        service.update(data["id"], {"status": "pending"})
        service.update(data["id"], {"status": "processing"})
        service.update(data["id"], {"status": "paid"})
        factory.cleanup(track_id)
        factory.cleanup_all(album_id, artist_id)


@pytest.mark.royalty
@allure.feature("Royalties")
class TestSideEffects(BaseAssertions):
    """Side effects test for royalties."""

    @allure.story("Paid royalty update artist total_earnings")
    def test_paid_royalty_update_artist_total_earnings(self, royalty_service, artist_service, album_service, track_service):
        """only valid transition 'pending' > paid/failed"""
        factory = TrackFactory(artist_service, album_service, track_service)
        #Create track  via factory
        track = factory.create()
        track_id = track["id"]
        album_id = track["album_id"]
        artist_id = track["artist_id"]

        service = royalty_service
        royalty = Royalty(artist_id=artist_id, track_id=track_id)
        payload = create_royalty_payload(royalty)
        response = service.create(payload)
        data = response.json()

        service.update(data["id"], {"status": "processing"})
        service.update(data["id"], {"status": "paid"})

        #get artist data
        get_response = artist_service.get_by_id(artist_id)

        self.using(get_response).assert_response_has_key_value("total_earnings", data["amount"])

        #CLEANUP
        factory.cleanup(track_id)
        factory.cleanup_all(album_id, artist_id)



