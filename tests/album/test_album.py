"""Test for Album API."""

import allure
import pytest

from tests.models.license_model import License
from tests.payloads.license_payloads import license_create_payload
from tests.base.base_assertions import BaseAssertions
from tests.payloads.album_payload import album_create_payload, album_update_payload
from tests.factories.artist_factory import ArtistFactory
from tests.schemas.album_schemas import ALBUM_RESPONSE_SCHEMA, ALBUM_LIST_SCHEMA
from tests.factories.track_factory import TrackFactory
from tests.factories.album_factory import AlbumFactory
from tests.factories.track_factory import TrackFactory
from tests.utils.constants import StatusCodes
from tests.utils.logger import get_logger

logger = get_logger(__name__)

@pytest.mark.album
@allure.feature("Albums")
class TestAlbumCreate(BaseAssertions):
    """Test for POST /albums - album registration.

    Validates that the album creation endpoint correctly handles
    valid input, missing fields valid data, and duplicate emails.
    """

    @allure.story("Create album successfully")
    def test_create_album_success(self, artist_service, album_service):
        """POST /albums - with all valid required fields should return 201
        and a response matching the Album Response schema.
        """
        #create artist via factory
        factory = ArtistFactory(artist_service)
        artist = factory.create()
        artist_id = artist["id"]

        #create album
        service = album_service
        payload = album_create_payload(artist_id=artist_id)

        response = service.create(payload)
        data = response.json()

        self.using(response).assert_status_code_is(StatusCodes.CREATED)
        self.using(response).assert_schema(ALBUM_RESPONSE_SCHEMA)
        self.using(response).assert_response_has_key("id")
        self.using(response).assert_response_key_absent("password")
        self.using(response).assert_response_key_absent("password_hash")
        self.using(response).assert_response_has_key_value("artist_id", payload["artist_id"])
        self.using(response).assert_response_has_key_value("title", payload["title"])

        #CLEANUP
        clean_response = service.delete_album(data["id"])
        assert clean_response.status_code == StatusCodes.OK

        factory.cleanup(artist_id)

    @allure.story("Create album with empty body")
    def test_create_album_missing_fields(self, album_service):
        """POST /albums - with empty body should return 400.
        with a message indicating which fields are missing.
        """

        response = album_service.create({})

        self.using(response).assert_status_code_is(StatusCodes.BAD_REQUEST)
        self.using(response).assert_response_has_key("message")


    @allure.story("Create album with empty required fields.")
    @pytest.mark.parametrize("field", ["artist_id", "title"])
    def test_create_album_empty_required_fields(self, artist_service, album_service, field):
        """POST /albums - with empty required fields should return 400,
        with message.
        """
        #create artist via factory
        factory = ArtistFactory(artist_service)
        artist = factory.create()
        artist_id = artist["id"]

        #create album
        service = album_service
        payload = album_create_payload(artist_id=artist_id)
        payload[field] = ""

        response = service.create(payload)

        self.using(response).assert_status_code_is(StatusCodes.BAD_REQUEST)
        self.using(response).assert_response_has_key("message")

        #CLEANUP
        factory.cleanup(artist_id)


    @allure.story("Create album with long title")
    def test_create_album_long_title(self, artist_service, album_service):
        """POST /albums - with long title should return 400,
        with a message.
        """
        #create artist via factory
        factory = ArtistFactory(artist_service)
        artist = factory.create()
        artist_id = artist["id"]

        #create album
        service = album_service
        payload = album_create_payload(artist_id=artist_id, title= "a" * 201)
        response = service.create(payload)

        self.using(response).assert_status_code_is(StatusCodes.BAD_REQUEST)
        self.using(response).assert_response_has_key("message")

        #CLEANUP
        factory.cleanup(artist_id)


    @allure.story("Create album with long description")
    def test_create_album_long_description(self, artist_service, album_service):
        """POST /albums - with long description should return 400,
        with a message.
        """
        #create artist via factory
        factory = ArtistFactory(artist_service)
        artist = factory.create()
        artist_id = artist["id"]

        #create album
        service = album_service
        payload = album_create_payload(artist_id=artist_id, description= "a" * 501)
        response = service.create(payload)

        self.using(response).assert_status_code_is(StatusCodes.BAD_REQUEST)
        self.using(response).assert_response_has_key("message")

        #CLEANUP
        factory.cleanup(artist_id)


    @allure.story("Create album with out of rage release_year")
    def test_create_album_out_range_release_year(self, artist_service, album_service):
        """POST /albums - with an out of range release_year return 400,
        with a message.
        """
        #create artist via factory
        factory = ArtistFactory(artist_service)
        artist = factory.create()
        artist_id = artist["id"]

        #create album
        service = album_service
        payload = album_create_payload(artist_id=artist_id, release_year= 1899)
        response = service.create(payload)

        self.using(response).assert_status_code_is(StatusCodes.BAD_REQUEST)
        self.using(response).assert_response_has_key("message")

        #CLEANUP

        factory.cleanup(artist_id)


    @allure.story("Create album with non-existent genre_id")
    def test_create_album_non_existent_genre_id(self, artist_service, album_service):
        """POST /albums - with non-existent genre_id should return 404,
        with a message.
        """
        #create artist via factory
        factory = ArtistFactory(artist_service)
        artist = factory.create()
        artist_id = artist["id"]

        #create album
        service = album_service
        payload = album_create_payload(artist_id=artist_id, genre_id= 999999)
        response = service.create(payload)

        self.using(response).assert_status_code_is(StatusCodes.NOT_FOUND)
        self.using(response).assert_response_has_key("message")

        #CLEANUP
        factory.cleanup(artist_id)


    @allure.story("Create album ignores client status")
    def test_create_album_status_is_always_draft(self, artist_service, album_service):
        """POST /albums - with a client-provided status should ignore the value
        and always create the album with draft status.
        """
        #create artist via factory
        factory = ArtistFactory(artist_service)
        artist = factory.create()
        artist_id = artist["id"]

        #create album
        service = album_service
        payload = album_create_payload(artist_id=artist_id, status="published")
        response = service.create(payload)
        data = response.json()
        logger.info("DATA %s", data)

        self.using(response).assert_status_code_is(StatusCodes.CREATED)
        self.using(response).assert_response_has_key_value("status", "draft")

        #CLEANUP
        factory.cleanup(artist_id)


    @allure.story("Create album with non-existent artist_id")
    def test_create_album_non_existent_artist_id(self, artist_service, album_service):
        """POST /albums - with non-existent artist_id should return 404,
        with a message.
        """
        #create album
        service = album_service
        payload = album_create_payload(artist_id=999999)
        response = service.create(payload)

        self.using(response).assert_status_code_is(StatusCodes.NOT_FOUND)
        self.using(response).assert_response_has_key("message")


@pytest.mark.album
@allure.feature("Albums")
class TestAlbumRetrieval(BaseAssertions):
    """GET /albums - GET/albums?artis_id= - GET /albums?status= - get /albums/<id>."""

    @allure.story("Get list of all albums")
    def test_get_list_albums(self, album_service):
        """GET /albums should return 200 with a list of albums."""

        response = album_service.list()

        self.using(response).assert_status_code_is(StatusCodes.OK)
        self.using(response).assert_schema(ALBUM_LIST_SCHEMA)


    @allure.story("Get list of all albums filtered by artist_id")
    def test_get_list_albums_filtered_artist_id(self, album_service, artist_service):
        """GET /albums?artist_id= - should return all albums for specific artist_id."""
        #Create album via Factory
        factory = AlbumFactory(artist_service, album_service)
        album = factory.create()
        artist_id = album["artist_id"]

        #GET album by artist_id
        get_response = album_service.list(artist_id=artist_id)
        get_data = get_response.json()

        self.using(get_response).assert_status_code_is(StatusCodes.OK)
        assert all(album["artist_id"] == artist_id for album in get_data)

        #CLEANUP
        album_service.delete_album(album["id"])
        factory.cleanup_all(artist_id)


    @allure.story("Get list of all albums filtered by status")
    def test_get_list_albums_filtered_status(self, album_service, artist_service):
        """GET /albums?artist_id= - should return all albums for specific status."""
        #Create album via Factory
        factory = AlbumFactory(artist_service, album_service)
        album = factory.create()
        artist_id = album["artist_id"]
        album_service.update(album["id"], {"status": "published"})

        #GET album by artist_id
        get_response = album_service.list(status="published")
        get_data = get_response.json()
        logger.info("DATA: %s", get_data)

        self.using(get_response).assert_status_code_is(StatusCodes.OK)
        assert all(album["status"] == "published" for album in get_data)

        #CLEANUP
        album_service.delete_album(album["id"])
        factory.cleanup_all(artist_id)


    @allure.story("Get album by ID.")
    def test_get_by_id(self, artist_service, album_service):
        """GET /albums/<id> - should return 200 and an album matching with album_id."""
        #Create album via Factory
        factory = AlbumFactory(artist_service, album_service)
        album = factory.create()
        artist_id = album["artist_id"]

        #GET album by artist_id
        response = album_service.get_by_id(album["id"])

        self.using(response).assert_status_code_is(StatusCodes.OK)
        self.using(response).assert_response_has_key_value("id", album["id"])
        self.using(response).assert_schema(ALBUM_RESPONSE_SCHEMA)

        #CLEANUP
        album_service.delete_album(album["id"])
        factory.cleanup_all(artist_id)


    @allure.story("Get nonexistent album.")
    def test_get_non_existent_album(self, album_service):
        """GET /albums/999999 - should return 400 and message."""

        response = album_service.get_by_id(999999)

        self.using(response).assert_status_code_is(StatusCodes.NOT_FOUND)
        self.using(response).assert_response_has_key("message")


@pytest.mark.album
@allure.feature("Albums")
class TestAlbumUpdate(BaseAssertions):
    """Test PUT /albums/<id>."""

    @allure.story("Update album success.")
    def test_update_album_success(self, artist_service, album_service):
        """PUT /albums/<id> - should update the provided fields and return 200.
        Only the specified fields change; others remain untouched.
        """
        #Create album via Factory
        factory = AlbumFactory(artist_service, album_service)
        album = factory.create()
        artist_id = album["artist_id"]

        #update
        update_payload = album_update_payload(
            description="Updated description for testing album updates.",
            status="archived",
            cover_url="https://beatflow.test/covers/the-marshall-mathers-lp-remastered.jpg"
        )
        update_response = album_service.update(album["id"], update_payload)

        self.using(update_response).assert_status_code_is(StatusCodes.OK)
        self.using(update_response).assert_response_has_key_value("title", album["title"])
        self.using(update_response).assert_response_has_key_value("release_year", album["release_year"])
        self.using(update_response).assert_response_has_key_value("description", update_payload["description"])
        self.using(update_response).assert_response_has_key_value("status", update_payload["status"])
        self.using(update_response).assert_response_has_key_value("cover_url", update_payload["cover_url"])

        #CLEANUP
        album_service.delete_album(album["id"])
        factory.cleanup_all(artist_id)


    @allure.story("Update nonexistent album.")
    def test_update_non_existent_album(self, album_service):
        """PUT /albums/999999 - should return 404 and message."""

        response = album_service.update(999999, {"description": "Updated description."})

        self.using(response).assert_status_code_is(StatusCodes.NOT_FOUND)
        self.using(response).assert_response_has_key("message")


@pytest.mark.album
@allure.feature("Albums")
class TestAlbumStateMachine(BaseAssertions):
    """TEST PUT /albums/<id> - for status machine transitions,
    draft -> published/archived
    published -> archived  -> TERMINAL
    """

    @allure.story("Transition status machine draft to archived")
    def test_draft_to_archived_transitions(self, artist_service, album_service):
        """PUT /albums/<id> - should return 200. with confirmed status machine 'archived'."""
        #Create album via Factory
        factory = AlbumFactory(artist_service, album_service)
        album = factory.create()
        artist_id = album["artist_id"]

        # transition status machine
        update_payload = album_update_payload(status="archived")
        update_response = album_service.update(album["id"], update_payload)

        self.using(update_response).assert_status_code_is(StatusCodes.OK)
        self.using(update_response).assert_response_has_key_value("status", "archived")

        #CLEANUP
        album_service.delete_album(album["id"])
        factory.cleanup_all(artist_id)


    @allure.story("Transition status machine draft to published")
    def test_draft_to_published_transitions(self, track_service, artist_service, album_service):
        """PUT /albums/<id> - should return 200. with status machine 'published'."""
        #Create album with track
        factory = TrackFactory(artist_service, album_service, track_service)
        track = factory.create()
        album_id = track["album_id"]

        #Update status to published
        response = album_service.update(album_id, {"status": "published"})
        self.using(response).assert_status_code_is(StatusCodes.OK)
        self.using(response).assert_response_has_key_value("status", "published")

        #CLEANUP
        album_service.update(album_id, {"status": "archived"})
        factory.cleanup(track["id"])
        factory.cleanup_all(track["album_id"], track["artist_id"])


    @allure.story("Transition status machine start in published")
    def test_published_to_archived_transitions(self, artist_service, album_service, track_service):
        """PUT /albums/<id> - should return 200. with status machine 'archived'."""
        #Create album with track
        factory = TrackFactory(artist_service, album_service, track_service)
        track = factory.create()
        album_id = track["album_id"]
        album_service.update(album_id, {"status": "published"})

        #Update status to archived
        response = album_service.update(album_id, {"status": "archived"})

        self.using(response).assert_status_code_is(StatusCodes.OK)
        self.using(response).assert_response_has_key_value("status", "archived")

        #CLEANUP
        factory.cleanup(track["id"])
        factory.cleanup_all(track["album_id"], track["artist_id"])


@pytest.mark.album
@allure.feature("Albums")
class TestAlbumDelete(BaseAssertions):
    """Test DELETE /albums/<id>."""

    @allure.story("Delete an album successfully")
    def test_delete_album_success(self, artist_service, album_service):
        """DELETE /albums/<id> - should return 200 and message."""
        #Create album via Factory
        factory = AlbumFactory(artist_service, album_service)
        album = factory.create()
        artist_id = album["artist_id"]

        #delete album
        response = album_service.delete_album(album["id"])

        self.using(response).assert_status_code_is(StatusCodes.OK)
        self.using(response).assert_response_has_key("message")

        #confirm
        get_response = album_service.get_by_id(album["id"])
        self.using(get_response).assert_status_code_is(StatusCodes.NOT_FOUND)

        #CLEANUP
        factory.cleanup_all(artist_id)


    @allure.story("Delete nonexistent album")
    def test_delete_non_existent_album(self, album_service):
        """DELETE /albums/999999 - should return 404 and message."""

        response = album_service.delete_album(999999)

        self.using(response).assert_status_code_is(StatusCodes.NOT_FOUND)
        self.using(response).assert_response_has_key("message")


    @allure.story("Delete album published")
    def test_delete_published_album(self, artist_service, album_service, track_service):
        """PUT /albums/<id> - with status 'published' should return 409. with message."""
        #create track via Factory
        factory = TrackFactory(artist_service, album_service, track_service)
        track = factory.create()
        track_id = track["id"]
        album_service.update(track["album_id"], {"status": "published"})

        response = album_service.delete_album(track["album_id"])

        self.using(response).assert_status_code_is(StatusCodes.CONFLICT)
        self.using(response).assert_response_has_key("message")

        #CLEANUP
        album_service.update(track["album_id"], {"status": "archived"})
        factory.cleanup(track_id)
        factory.cleanup_all(track["album_id"], track["artist_id"])


    @allure.story("delete album with licensed tracks")
    def test_delete_album_with_licensed_tracks(self, artist_service, album_service, track_service, license_service):
        """PUT /albums/<id> - with status 'published' should return 409. with message."""
        #create track via Factory
        factory = TrackFactory(artist_service, album_service, track_service)
        track = factory.create()
        track_id = track["id"]
        album_id = track["album_id"]
        artist_id = track["artist_id"]

        #create license
        service = license_service
        license = License(track_id=track_id)
        payload = license_create_payload(license)
        response = service.create(payload)
        data = response.json()

        #delete album
        delete_response = album_service.delete_album(album_id)

        self.using(delete_response).assert_status_code_is(StatusCodes.CONFLICT)

        #CLEANUP
        license_service.update(data["id"], {"status": "revoked", "revocation_reason": "revocation reason"})
        album_service.update(album_id, {"status": "archived"})
        factory.cleanup(track_id)
        factory.cleanup_all(album_id, artist_id)

