"""Test for Track API."""

import allure
import pytest

from tests.base.base_assertions import BaseAssertions
from tests.models.royalty_model import Royalty
from tests.models.license_model import License
from tests.payloads.license_payloads import license_create_payload
from tests.payloads.royalty_payload import create_royalty_payload
from tests.payloads.album_payload import album_update_payload
from tests.payloads.track_payload import track_create_payload, track_update_payload
from tests.schemas.track_schemas import TRACK_RESPONSE_SCHEMA, TRACK_LIST_SCHEMA
from tests.factories.album_factory import AlbumFactory
from tests.factories.track_factory import TrackFactory
from tests.utils.constants import StatusCodes, MusicGenres
from tests.utils.logger import get_logger

logger = get_logger(__name__)

@pytest.mark.track
@allure.feature("Tracks")
class TestTrackCreate(BaseAssertions):
    """Test for POST /tracks - track registration.

    Validates that the track creation endpoint correctly handles.
    Valid input, missing fields valid data.
    """

    @allure.story("Create track successfully")
    def test_create_track_success(self, artist_service, album_service, track_service):
        """POST /tracks - with valid required fields should return 201.
        and a response matching the Track Response schema.
        """
        #create album via Factory
        factory = AlbumFactory(artist_service, album_service)
        album = factory.create()
        album_id = album["id"]
        artist_id = album["artist_id"]

        #create track
        service = track_service
        payload = track_create_payload(album_id=album_id)
        response = service.create(payload)
        data = response.json()

        self.using(response).assert_status_code_is(StatusCodes.CREATED)
        self.using(response).assert_schema(TRACK_RESPONSE_SCHEMA)
        self.using(response).assert_response_has_key_value("album_id", album_id)


        #CLEANUP
        clean_response = service.delete_track(data["id"])
        assert clean_response.status_code == StatusCodes.OK
        factory.cleanup(album_id)
        factory.cleanup_all(artist_id)


    @pytest.mark.parametrize("length_title", ["", "a" * 201])
    @allure.story("Create track title boundary values")
    def test_create_track_title_boundary_values(self,artist_service, album_service, track_service, length_title):
        """POST /tracks - with title boundary values should return 400,
        with message.
        """
        #create album via Factory
        factory = AlbumFactory(artist_service, album_service)
        album = factory.create()
        album_id = album["id"]
        artist_id = album["artist_id"]

        #create track
        service = track_service
        payload = track_create_payload(album_id=album_id, title=length_title)
        response = service.create(payload)

        self.using(response).assert_status_code_is(StatusCodes.BAD_REQUEST)
        self.using(response).assert_response_has_key("message")

        #CLEANUP

        factory.cleanup(album_id)
        factory.cleanup_all(artist_id)


    @allure.story("Create track with nonexistent album")
    def test_create_track_with_nonexistent_album(self,artist_service, album_service, track_service):
        """POST /tracks - with nonexistent album, should return 400
        and message.
        """
        service = track_service
        payload = track_create_payload(album_id=999999)
        response = service.create(payload)

        self.using(response).assert_status_code_is(StatusCodes.NOT_FOUND)
        self.using(response).assert_response_has_key("message")


    @allure.story("Create track with archived album")
    def test_create_track_with_archived_album(self,artist_service, album_service, track_service):
        """POST /tracks - with archived album, should return 400
        and message."""
        #create album via Factory
        factory = AlbumFactory(artist_service, album_service)
        album = factory.create()
        album_id = album["id"]
        artist_id = album["artist_id"]

        update_album_response = album_service.update(album_id, album_update_payload(status="archived"))
        logger.info("DATA: %s", update_album_response.json())
        assert update_album_response.status_code == StatusCodes.OK

        #create track
        service = track_service
        payload = track_create_payload(album_id=album_id)
        response = service.create(payload)

        self.using(response).assert_status_code_is(StatusCodes.BAD_REQUEST)
        self.using(response).assert_response_has_key("message")


        #CLEANUP

        factory.cleanup(album_id)
        factory.cleanup_all(artist_id)


    @pytest.mark.parametrize("time", [29, 3601])
    @allure.story("Create track duration_seconds boundary values")
    def test_create_track_duration_seconds_boundary_values(self,artist_service, album_service, track_service, time):
        """POST /tracks - with duration_seconds boundary values should return 400,
        and message.
        """
        #create album via Factory
        factory = AlbumFactory(artist_service, album_service)
        album = factory.create()
        album_id = album["id"]
        artist_id = album["artist_id"]

        #create track
        service = track_service
        payload = track_create_payload(album_id=album_id, duration_seconds=time)
        response = service.create(payload)

        self.using(response).assert_status_code_is(StatusCodes.BAD_REQUEST)
        self.using(response).assert_response_has_key("message")

        #CLEANUP

        factory.cleanup(album_id)
        factory.cleanup_all(artist_id)


    @pytest.mark.parametrize("new_number", [0, 51])
    @allure.story("Create track track_numer boundary values")
    def test_create_track_with_track_number_boundary_values(self,artist_service, album_service, track_service, new_number):
        """POST /tracks - with track_number boundary values should return 400,
        and message.
        """
        #create album via Factory
        factory = AlbumFactory(artist_service, album_service)
        album = factory.create()
        album_id = album["id"]
        artist_id = album["artist_id"]

        #create track
        service = track_service
        payload = track_create_payload(album_id=album_id, track_number=new_number)
        response = service.create(payload)

        self.using(response).assert_status_code_is(StatusCodes.BAD_REQUEST)
        self.using(response).assert_response_has_key("message")

        #CLEANUP

        factory.cleanup(album_id)
        factory.cleanup_all(artist_id)


    @allure.story("Create two tracks with same track_number ")
    def test_create_two_tracks_with_same_track_number(self,artist_service, album_service, track_service):
        """POST /tracks - two tracks with same tracks_number, should return 409
        and message.
        """
        #create album via Factory
        factory = AlbumFactory(artist_service, album_service)
        album = factory.create()
        album_id = album["id"]
        artist_id = album["artist_id"]

        track_number = 1

        #create first track
        service = track_service
        payload = track_create_payload(album_id=album_id, track_number=track_number)
        response = service.create(payload)
        data = response.json()

        #create second track
        payload_2 = track_create_payload(album_id=album_id, track_number=track_number)
        response_2 = service.create(payload_2)

        self.using(response_2).assert_status_code_is(StatusCodes.CONFLICT)
        self.using(response_2).assert_response_has_key("message")


        #CLEANUP
        clean_response = service.delete_track(data["id"])
        assert clean_response.status_code == StatusCodes.OK
        factory.cleanup(album_id)
        factory.cleanup_all(artist_id)


    @allure.story("Create track with nonexistent genre_id")
    def test_create_track_with_nonexistent_genre_id(self,artist_service, album_service, track_service):
        """POST /tracks - with nonexistent genre_id should return 404,
        with message.
        """
        #create album via Factory
        factory = AlbumFactory(artist_service, album_service)
        album = factory.create()
        album_id = album["id"]
        artist_id = album["artist_id"]

        #create track
        service = track_service
        payload = track_create_payload(album_id=album_id, genre_id=11)
        response = service.create(payload)

        self.using(response).assert_status_code_is(StatusCodes.NOT_FOUND)
        self.using(response).assert_response_has_key("message")

        #CLEANUP
        factory.cleanup(album_id)
        factory.cleanup_all(artist_id)


    @allure.story("Create track with default is_available value")
    def test_create_track_default_is_available(self,artist_service, album_service, track_service):
        """POST /tracks - should return 201.
        and set is_available to True by default.
        """
        #create album via Factory
        factory = AlbumFactory(artist_service, album_service)
        album = factory.create()
        album_id = album["id"]
        artist_id = album["artist_id"]

        #create track
        service = track_service
        payload = track_create_payload(album_id=album_id)
        response = service.create(payload)
        data = response.json()

        self.using(response).assert_status_code_is(StatusCodes.CREATED)
        self.using(response).assert_response_has_key_value("is_available", True)


        #CLEANUP
        clean_response = service.delete_track(data["id"])
        assert clean_response.status_code == StatusCodes.OK
        factory.cleanup(album_id)
        factory.cleanup_all(artist_id)


    @allure.story("Create track with default is_explicit value")
    def test_create_track_default_is_explicit(self,artist_service, album_service, track_service):
        """POST /tracks - should return 201.
        and set is_explicit to False by default.
        """
        #create album via Factory
        factory = AlbumFactory(artist_service, album_service)
        album = factory.create()
        album_id = album["id"]
        artist_id = album["artist_id"]

        #create track
        service = track_service
        payload = track_create_payload(album_id=album_id)
        response = service.create(payload)
        data = response.json()

        self.using(response).assert_status_code_is(StatusCodes.CREATED)
        self.using(response).assert_response_has_key_value("is_explicit", False)


        #CLEANUP
        clean_response = service.delete_track(data["id"])
        assert clean_response.status_code == StatusCodes.OK
        factory.cleanup(album_id)
        factory.cleanup_all(artist_id)


    @allure.story("Create track with default play_count value")
    def test_create_track_default_play_count(self,artist_service, album_service, track_service):
        """POST /tracks - should return 201.
        and set play_count to 0 by default.
        """
        #create album via Factory
        factory = AlbumFactory(artist_service, album_service)
        album = factory.create()
        album_id = album["id"]
        artist_id = album["artist_id"]

        #create track
        service = track_service
        payload = track_create_payload(album_id=album_id)
        response = service.create(payload)
        data = response.json()

        self.using(response).assert_status_code_is(StatusCodes.CREATED)
        self.using(response).assert_response_has_key_value("play_count", 0)


        #CLEANUP
        clean_response = service.delete_track(data["id"])
        assert clean_response.status_code == StatusCodes.OK
        factory.cleanup(album_id)
        factory.cleanup_all(artist_id)


@pytest.mark.track
@allure.feature("Tracks")
class TestTracksRetrieval(BaseAssertions):
    """Test for GET /tracks - GET /tracks/<id>
    GET /tracks?album_id= - GET /tracks=genre_id - GET /tracks=is_available
    """

    @allure.story("Get tracks list")
    def test_get_tracks_list(self, track_service):
        """GET /tracks - should return 200 with a list of all active tracks"""

        response = track_service.list()
        data = response.json()
        logger.info("DATA: %s", data)

        self.using(response).assert_status_code_is(StatusCodes.OK)
        self.using(response).assert_schema(TRACK_LIST_SCHEMA)


    @allure.story("Get track by id")
    def test_get_by_id(self,artist_service, album_service, track_service):
        """POST /tracks - should return 200.
        with a track matching by id.
        """
        #create album via Factory
        factory = AlbumFactory(artist_service, album_service)
        album = factory.create()
        album_id = album["id"]
        artist_id = album["artist_id"]

        #create track
        service = track_service
        payload = track_create_payload(album_id=album_id)
        response = service.create(payload)
        data = response.json()

        #get by id
        get_response = service.get_by_id(data["id"])

        self.using(get_response).assert_status_code_is(StatusCodes.OK)
        self.using(get_response).assert_schema(TRACK_RESPONSE_SCHEMA)
        self.using(get_response).assert_response_has_key_value("id", data["id"])

        #CLEANUP
        clean_response = service.delete_track(data["id"])
        assert clean_response.status_code == StatusCodes.OK
        factory.cleanup(album_id)
        factory.cleanup_all(artist_id)


    @allure.story("Get list tracks filtered by album_id ")
    def test_get_filtered_by_album_id(self,artist_service, album_service, track_service):
        """POST /tracks?album_id=  - should return 200.
        with a tracks matching by album_id.
        """
        #create first album via Factory
        factory = AlbumFactory(artist_service, album_service)
        album = factory.create()
        album_id = album["id"]
        artist_id = album["artist_id"]

        service = track_service

        #create track
        payload_1 = track_create_payload(album_id=album_id)
        response_1 = service.create(payload_1)
        data_1 = response_1.json()

        #create second album via Factory
        album_2 = factory.create(title="The Eminem Show",
                                 description="Fourth studio album by Eminem, released in 2002.",
                                 release_year=2002,
                                 genre_id=MusicGenres.HIP_HOP,
                                 status="published",
                                 cover_url="https://beatflow.test/covers/the-eminem-show.jpg")
        album_id_2 = album_2["id"]


        #create track album 2
        payload_2 = track_create_payload(album_id=album_id_2,
                                        title="Without Me",
                                        duration_seconds=290,
                                        track_number=10,
                                        genre_id=MusicGenres.HIP_HOP,
                                        is_explicit=True)
        response_2 = service.create(payload_2)
        data_2 = response_2.json()

        #get list filtered by album_id
        get_response = service.list(album_id_2)
        get_data = get_response.json()
        logger.info("DATA: %s", get_data)

        self.using(get_response).assert_status_code_is(StatusCodes.OK)
        assert all(track["album_id"] == album_id_2 for track in get_data)

        #CLEANUP
        clean_response = service.delete_track(data_1["id"])
        assert clean_response.status_code == StatusCodes.OK

        clean_response = service.delete_track(data_2["id"])
        assert clean_response.status_code == StatusCodes.OK

        factory.cleanup(album_id)
        factory.cleanup(album_id_2)

        factory.cleanup_all(artist_id)


    @allure.story("Get list tracks filtered by genre_id")
    def test_get_filtered_by_genre_id(self,artist_service, album_service, track_service):
        """POST /tracks?genre_id=  - should return 200.
        with a tracks matching by genre_id.
        """
        #create album via Factory
        factory = AlbumFactory(artist_service, album_service)
        album = factory.create()
        album_id = album["id"]
        artist_id = album["artist_id"]

        service = track_service

        #create track 2
        payload_1 = track_create_payload(album_id=album_id)
        response_1 = service.create(payload_1)
        data_1 = response_1.json()

        #create track 2
        payload_2 = track_create_payload(album_id=album_id,
                                         title="Love the Way You Lie",
                                         duration_seconds=263,
                                         track_number=15,
                                         genre_id=MusicGenres.POP,
                                         is_explicit=True)
        response_2 = service.create(payload_2)
        data_2 = response_2.json()

        #get list filtered by genre_id
        get_response = service.list(genre_id=MusicGenres.POP)
        get_data = get_response.json()
        logger.info("DATA: %s", get_data)

        self.using(get_response).assert_status_code_is(StatusCodes.OK)
        assert all(track["genre_id"] == MusicGenres.POP for track in get_data)

        #CLEANUP
        clean_response = service.delete_track(data_1["id"])
        assert clean_response.status_code == StatusCodes.OK

        clean_response = service.delete_track(data_2["id"])
        assert clean_response.status_code == StatusCodes.OK

        factory.cleanup(album_id)
        factory.cleanup_all(artist_id)


    @allure.story("Get list tracks filtered by is_available")
    def test_get_filtered_by_is_available(self,artist_service, album_service, track_service):
        """POST /tracks?is_available=  - should return 200.
        with a tracks matching by is_available.
        """
        #create album via Factory
        factory = AlbumFactory(artist_service, album_service)
        album = factory.create()
        album_id = album["id"]
        artist_id = album["artist_id"]

        service = track_service

        #create track 2
        payload_1 = track_create_payload(album_id=album_id)
        response_1 = service.create(payload_1)
        data_1 = response_1.json()
        logger.info("DATA TRACK 1: %s", data_1)

        #create track 2
        payload_2 = track_create_payload(album_id=album_id,
                                         title="Love the Way You Lie",
                                         duration_seconds=263,
                                         track_number=15,
                                         genre_id=MusicGenres.POP,
                                         is_available=False,
                                         is_explicit=True)
        response_2 = service.create(payload_2)
        data_2 = response_2.json()

        #get list filtered by is_available
        get_response = service.list(is_available=True)
        get_data = get_response.json()
        logger.info("DATA: %s", get_data)

        self.using(get_response).assert_status_code_is(StatusCodes.OK)
        assert all(track["is_available"] == True for track in get_data)

        #CLEANUP
        clean_response = service.delete_track(data_1["id"])
        assert clean_response.status_code == StatusCodes.OK

        clean_response = service.delete_track(data_2["id"])
        assert clean_response.status_code == StatusCodes.OK

        factory.cleanup(album_id)
        factory.cleanup_all(artist_id)


    @allure.story("Get nonexistent track")
    def test_get_non_existent_tracks(self, track_service):
        """GET /tracks/999999 - should return 404 with message"""

        response = track_service.get_by_id(999999)
        data = response.json()

        self.using(response).assert_status_code_is(StatusCodes.NOT_FOUND)
        self.using(response).assert_response_has_key("message")


@pytest.mark.track
@allure.feature("Tracks")
class TestUpdateTrack(BaseAssertions):
    """Tests for PUT /tracks/id."""

    @allure.story("Update a track successfully")
    def test_update_success(self, artist_service, album_service, track_service):
        """PUT /track/<id> should update the provided fields and return200.
        Only the specified fields change, others remain untouched.
        """
        #create album via Factory
        factory = AlbumFactory(artist_service, album_service)
        album = factory.create()
        album_id = album["id"]
        artist_id = album["artist_id"]

        #create track
        service = track_service
        payload = track_create_payload(album_id=album_id)
        response = service.create(payload)
        data = response.json()

        #update track
        update_payload = track_update_payload(title="Stan (Remastered)",
                                              duration_seconds=410,
                                              track_number=5,
                                              genre_id=MusicGenres.POP,
                                              is_available=False,
                                              is_explicit=True)
        update_response = service.update(data["id"], update_payload)

        self.using(update_response).assert_status_code_is(StatusCodes.OK)
        self.using(update_response).assert_response_has_key_value("title", update_payload["title"])
        self.using(update_response).assert_response_has_key_value("duration_seconds", update_payload["duration_seconds"])
        self.using(update_response).assert_response_has_key_value("track_number", update_payload["track_number"])
        self.using(update_response).assert_response_has_key_value("genre_id", update_payload["genre_id"])
        self.using(update_response).assert_response_has_key_value("is_available", update_payload["is_available"])
        self.using(update_response).assert_response_has_key_value("is_explicit", update_payload["is_explicit"])

        #CLEANUP
        clean_response = service.delete_track(data["id"])
        assert clean_response.status_code == StatusCodes.OK
        factory.cleanup(album_id)
        factory.cleanup_all(artist_id)


    @allure.story("Update nonexistent track")
    def test_update_nonexistent_track(self, track_service):
        """PUT /track/999999 should return 404,
        with message.
        """
        #update track

        update_payload = track_update_payload(title="Stan (Remastered)")
        update_response = track_service.update(999999, update_payload)

        self.using(update_response).assert_status_code_is(StatusCodes.NOT_FOUND)
        self.using(update_response).assert_response_has_key("message")


    @allure.story("Update track with empty payload")
    def test_update_with_empty_payload(self, artist_service, album_service, track_service):
        """PUT /track/<id> - with empty update payload should return 400,
        with message.
        """
        #create album via Factory
        factory = AlbumFactory(artist_service, album_service)
        album = factory.create()
        album_id = album["id"]
        artist_id = album["artist_id"]

        #create track 1
        service = track_service
        payload = track_create_payload(album_id=album_id)
        response = service.create(payload)
        data = response.json()

        #update track
        update_payload = {}
        update_response = track_service.update(data["id"], update_payload)

        self.using(update_response).assert_status_code_is(StatusCodes.BAD_REQUEST)
        self.using(update_response).assert_response_has_key("message")

        #CLEANUP
        clean_response = service.delete_track(data["id"])
        assert clean_response.status_code == StatusCodes.OK
        factory.cleanup(album_id)
        factory.cleanup_all(artist_id)

    @allure.story("Update a track with another track_number")
    def test_update_track_with_another_track_number(self, artist_service, album_service, track_service):
        """PUT /track/<id> - try update a track change the track_number already exist
        should return 409 with message.
        """
        #create album via Factory
        factory = AlbumFactory(artist_service, album_service)
        album = factory.create()
        album_id = album["id"]
        artist_id = album["artist_id"]

        #create track 1
        service = track_service
        payload_1 = track_create_payload(album_id=album_id)
        response_1 = service.create(payload_1)
        data_1 = response_1.json()

        #create track 2
        payload_2 = track_create_payload(album_id=album_id,
                                         title="The Real Slim Shady",
                                         duration_seconds=284,
                                         track_number=7,
                                         genre_id=MusicGenres.HIP_HOP)
        response_2 = service.create(payload_2)
        data_2 = response_2.json()


        #update track 1
        update_payload = track_update_payload(title="Stan (Remastered)", track_number=3)
        update_response = service.update(data_2["id"], update_payload)

        self.using(update_response).assert_status_code_is(StatusCodes.CONFLICT)
        self.using(update_response).assert_response_has_key("message")


        #CLEANUP
        clean_response_1 = service.delete_track(data_1["id"])
        assert clean_response_1.status_code == StatusCodes.OK

        clean_response_2 = service.delete_track(data_2["id"])
        assert clean_response_2.status_code == StatusCodes.OK

        factory.cleanup(album_id)
        factory.cleanup_all(artist_id)

@pytest.mark.track
@allure.feature("Tracks")
class TestDeleteTrack(BaseAssertions):
    """Tests for DELETE /tracks/<id>."""

    @allure.story("Delete a track successfully")
    def test_delete_success(self, track_service, album_service, artist_service):
        """DELETE /tracks/<id> - should return 200 and message.
        the track should not persist in tracks list
        """
        #create album via Factory
        factory = AlbumFactory(artist_service, album_service)
        album = factory.create()
        album_id = album["id"]
        artist_id = album["artist_id"]

        service = track_service

        #create track
        payload = track_create_payload(album_id=album_id)
        response = service.create(payload)
        data = response.json()

        #delete track
        delete_response = service.delete_track(data["id"])

        self.using(delete_response).assert_status_code_is(StatusCodes.OK)
        self.using(delete_response).assert_response_has_key("message")

        #confirm deleting
        get_response = service.get_by_id(data["id"])

        self.using(get_response).assert_status_code_is(StatusCodes.NOT_FOUND)

        #CLEANUP
        factory.cleanup(album_id)
        factory.cleanup_all(artist_id)


    @allure.story("Delete nonexistent track")
    def test_delete_nonexistent_track(self, track_service, album_service, artist_service):
        """DELETE /tracks/999999 - should return 404 and message."""

        response = track_service.delete_track(999999)

        self.using(response).assert_status_code_is(StatusCodes.NOT_FOUND)
        self.using(response).assert_response_has_key("message")



    @allure.story("Delete track with active license")
    def test_delete_track_with_active_license(self, track_service, album_service, artist_service, license_service):
        """DELETE /tracks/<id> - with active license should return 409 and message."""
        #create track via Factory
        factory = TrackFactory(artist_service, album_service, track_service)
        track = factory.create()
        track_id = track["id"]

        #create license
        service = license_service
        license = License(track_id=track_id)
        payload = license_create_payload(license)
        response = service.create(payload)
        data = response.json()

        delete_response = track_service.delete_track(track_id)

        self.using(delete_response).assert_status_code_is(StatusCodes.CONFLICT)

        #CLEANUP
        service.update(data["id"], {"status": "revoked", "revocation_reason": "revocation reason"})
        factory.cleanup(track_id)
        factory.cleanup_all(track["album_id"],track["artist_id"])


    @allure.story("Delete track with pending royalties")
    def test_delete_track_with_pending_royalties(self, track_service, album_service, artist_service, royalty_service):
        """DELETE /tracks/<id> - with pending royalties should return 409 and message."""
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

        delete_response = track_service.delete_track(track_id)

        self.using(delete_response).assert_status_code_is(StatusCodes.CONFLICT)

        #CLEANUP
        service.update(data["id"], {"status": "processing"})
        service.update(data["id"], {"status": "paid"})
        factory.cleanup(track_id)
        factory.cleanup_all(album_id, artist_id)