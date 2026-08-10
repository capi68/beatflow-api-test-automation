"""Test for Playlist track API."""

import allure
import  pytest

from tests.base.base_assertions import BaseAssertions
from tests.payloads.track_payload import track_update_payload
from tests.payloads.playlist_track_payload import playlist_track_create_payload, playlist_track_update_payload
from tests.schemas.playlist_track_schemas import PLAYLIST_TRACK_RESPONSE_SCHEMA, PLAYLIST_TRACK_GET_RESPONSE_SCHEMA
from tests.models.playlist_track_model import PlaylistTrack
from tests.factories.playlist_factory import PlaylistFactory
from tests.factories.playlist_track_factory import PlaylistTrackFactory
from tests.factories.track_factory import TrackFactory
from tests.services.playlist_track_service import PlaylistTrackService
from tests.utils.constants import StatusCodes
from tests.utils.logger import get_logger

logger = get_logger(__name__)

@pytest.mark.playlist_track
@allure.feature("Playlist Tracks")
class TestPlaylistTrackCreation(BaseAssertions):
    """Test for POST /playlist-tracks - playlist track registration,
    validates that the creation endpoint correctly handless,
    valid input, missing fields, valid data.
    """

    @allure.story("Create playlist track successfully")
    def test_create_playlist_track_success(self, playlist_service, listener_service, artist_service, album_service, track_service, playlist_track_service):
        """POST /playlist-tracks - with valid data required fields should return 201;
        and response matching with Playlist Track Response Schema.
        """
        #Create playlist via Factory
        playlist_factory = PlaylistFactory(listener_service, playlist_service)
        playlist = playlist_factory.create()
        playlist_id = playlist["id"]
        listener_id = playlist["listener_id"]

        #Create track via Factory
        track_factory = TrackFactory(artist_service, album_service, track_service)
        track = track_factory.create()
        track_id = track["id"]
        album_id = track["album_id"]
        artist_id = track["artist_id"]

        service = playlist_track_service

        #Registration playlist Track
        playlist_track = PlaylistTrack(playlist_id=playlist_id, track_id=track_id)
        payload = playlist_track_create_payload(playlist_track)

        response = service.create(payload)
        data = response.json()

        self.using(response).assert_status_code_is(StatusCodes.CREATED)
        self.using(response).assert_schema(PLAYLIST_TRACK_RESPONSE_SCHEMA)
        self.using(response).assert_response_has_key("id")
        self.using(response).assert_response_has_key("position")

        #CLEANUP
        clean_response = service.delete_playlist_track(data["id"])
        assert clean_response.status_code == StatusCodes.OK

        track_factory.cleanup(track_id)
        track_factory.cleanup_all(album_id, artist_id)

        playlist_factory.cleanup(playlist_id)
        playlist_factory.cleanup_all(listener_id)



    @allure.story("Create playlist track with empty body")
    def test_create_playlist_track_missing_fields(self, playlist_service, listener_service, artist_service, album_service, track_service, playlist_track_service):
        """POST /playlist-tracks - with missing required fields should return 400
        and message.
        """
        service = playlist_track_service

        #Registration playlist Track
        response = service.create({})

        self.using(response).assert_status_code_is(StatusCodes.BAD_REQUEST)
        self.using(response).assert_response_has_key("message")


    @allure.story("Create playlist track empty required fields")
    @pytest.mark.parametrize("field", ["playlist_id", "track_id"])
    def test_create_playlist_track_empty_required_fields(self, playlist_service, listener_service, artist_service, album_service, track_service, playlist_track_service, field):
        """POST /playlist-tracks - with empty required fields should return 400
        and message.
        """
        #Create playlist via Factory
        playlist_factory = PlaylistFactory(listener_service, playlist_service)
        playlist = playlist_factory.create()
        playlist_id = playlist["id"]
        listener_id = playlist["listener_id"]

        #Create track via Factory
        track_factory = TrackFactory(artist_service, album_service, track_service)
        track = track_factory.create()
        track_id = track["id"]
        album_id = track["album_id"]
        artist_id = track["artist_id"]

        service = playlist_track_service

        #Registration playlist Track
        playlist_track = PlaylistTrack(playlist_id=playlist_id, track_id=track_id)
        payload = playlist_track_create_payload(playlist_track)
        payload[field] = ""

        response = service.create(payload)
        data = response.json()

        self.using(response).assert_status_code_is(StatusCodes.BAD_REQUEST)
        self.using(response).assert_response_has_key("message")

        #CLEANUP

        track_factory.cleanup(track_id)
        track_factory.cleanup_all(album_id, artist_id)

        playlist_factory.cleanup(playlist_id)
        playlist_factory.cleanup_all(listener_id)



    @allure.story("Create playlist unavailable track")
    def test_create_playlist_unavailable_track(self, playlist_service, listener_service, artist_service, album_service, track_service, playlist_track_service):
        """POST /playlist-tracks - with unavailable track should return 400
        and message.
        """
        #Create playlist via Factory
        playlist_factory = PlaylistFactory(listener_service, playlist_service)
        playlist = playlist_factory.create()
        playlist_id = playlist["id"]
        listener_id = playlist["listener_id"]

        #Create track via Factory
        track_factory = TrackFactory(artist_service, album_service, track_service)
        track = track_factory.create()
        track_id = track["id"]
        album_id = track["album_id"]
        artist_id = track["artist_id"]

        #update track >> is_available: False
        track_service.update(track_id, track_update_payload(is_available=False))

        service = playlist_track_service

        #Registration playlist Track
        playlist_track = PlaylistTrack(playlist_id=playlist_id, track_id=track_id)
        payload = playlist_track_create_payload(playlist_track)

        response = service.create(payload)
        data = response.json()

        self.using(response).assert_status_code_is(StatusCodes.BAD_REQUEST)
        self.using(response).assert_response_has_key("message")

        #CLEANUP

        track_factory.cleanup(track_id)
        track_factory.cleanup_all(album_id, artist_id)

        playlist_factory.cleanup(playlist_id)
        playlist_factory.cleanup_all(listener_id)


    @allure.story("Prevent duplicate track in playlist.")
    def test_create_playlist_duplicate_track(self, playlist_service, listener_service, artist_service, album_service, track_service, playlist_track_service):
        """POST /playlist-tracks - duplicate track should return 409;
        and message.
        """
        #Create playlist via Factory
        playlist_factory = PlaylistFactory(listener_service, playlist_service)
        playlist = playlist_factory.create()
        playlist_id = playlist["id"]
        listener_id = playlist["listener_id"]

        #Create track via Factory
        track_factory = TrackFactory(artist_service, album_service, track_service)
        track = track_factory.create()
        track_id = track["id"]
        album_id = track["album_id"]
        artist_id = track["artist_id"]

        service = playlist_track_service

        #Registration playlist Track
        playlist_track = PlaylistTrack(playlist_id=playlist_id, track_id=track_id)
        payload = playlist_track_create_payload(playlist_track)

        response = service.create(payload)
        data = response.json()

        self.using(response).assert_status_code_is(StatusCodes.CREATED)

        #second registration
        playlist_track_2 = PlaylistTrack(playlist_id=playlist_id, track_id=track_id)
        payload_2 = playlist_track_create_payload(playlist_track_2)

        response_2 = service.create(payload_2)
        data_2 = response.json()

        self.using(response_2).assert_status_code_is(StatusCodes.CONFLICT)
        self.using(response_2).assert_response_has_key("message")


        #CLEANUP
        clean_response = service.delete_playlist_track(data["id"])
        assert clean_response.status_code == StatusCodes.OK

        track_factory.cleanup(track_id)
        track_factory.cleanup_all(album_id, artist_id)

        playlist_factory.cleanup(playlist_id)
        playlist_factory.cleanup_all(listener_id)


    @allure.story("Exceed max number of tracks per playlist.")
    def test_create_playlist_exceed_tracks(self, playlist_service, listener_service, artist_service, album_service, track_service, playlist_track_service):
        """POST /playlist-tracks - with more of 100 tracks per playlist;
        should return 400 and message.
        """
        #Create playlist via Factory
        playlist_factory = PlaylistFactory(listener_service, playlist_service)
        playlist = playlist_factory.create()
        playlist_id = playlist["id"]
        listener_id = playlist["listener_id"]

        service = playlist_track_service

        #Create 100 tracks via Factory
        track_factory = TrackFactory(artist_service, album_service, track_service)
        resources = []
        for i in range(100):
            track = track_factory.create(title=f"Track_number_{i}")
            track_id = track["id"]
            album_id= track["album_id"]
            artist_id = track["artist_id"]
            resources.append({
                "track_id": track_id,
                "album_id": album_id,
                "artist_id": artist_id
            })

            #Registration playlist Track
            playlist_track = PlaylistTrack(playlist_id=playlist_id, track_id=track_id)
            payload = playlist_track_create_payload(playlist_track)
            response = service.create(payload)


        #Create and add track 101
        track_101 = track_factory.create(title=f"Track_number_101")
        track_101_id = track_101["id"]
        album_101_id = track_101["album_id"]
        artist_101_id = track_101["artist_id"]
        playlist_track_101 = PlaylistTrack(playlist_id=playlist_id, track_id=track_101_id)
        payload_101 = playlist_track_create_payload(playlist_track_101)

        response_101 = service.create(payload_101)
        resources.append({
            "track_id": track_101_id,
            "album_id": album_101_id,
            "artist_id": artist_101_id
        })

        self.using(response_101).assert_status_code_is(StatusCodes.BAD_REQUEST)
        self.using(response_101).assert_response_has_key("message")


        #CLEANUP
        for resource in resources:
            track_factory.cleanup(resource["track_id"])
            track_factory.cleanup_all(resource["album_id"], resource["artist_id"])


        playlist_factory.cleanup(playlist_id)
        playlist_factory.cleanup_all(listener_id)


@pytest.mark.playlist_track
@allure.feature("Playlist Tracks")
class TestPlaylistTrackRetrieval(BaseAssertions):
    """Test for GET /playlist-tracks - GET /playlist-tracks/<id>"""

    @allure.story("Get list of playlist tracks")
    def test_list_playlist_track(self, listener_service, playlist_service, artist_service, album_service, track_service, playlist_track_service):
        """GET /playlist-tracks - should return 200 with  a list of tracks
        in a specified playlist"""
        #Create playlist_track via Factory
        factory = PlaylistTrackFactory(playlist_track_service, playlist_service, listener_service, artist_service, album_service, track_service)
        playlist_track = factory.create()
        playlist_track_id = playlist_track["id"]
        playlist_id = playlist_track["playlist_id"]

        service = playlist_track_service

        #GET list
        get_response = playlist_track_service.list(playlist_id)
        get_data = get_response.json()

        self.using(get_response).assert_status_code_is(StatusCodes.OK)
        self.using(get_response).assert_schema(PLAYLIST_TRACK_GET_RESPONSE_SCHEMA)
        assert all(tracks["playlist_id"] == playlist_id for tracks in get_data)

        #CLEANUP
        factory.cleanup(playlist_track_id)
        factory.cleanup_all(
            playlist_track["track_id"],
            playlist_track["album_id"],
            playlist_track["artist_id"],
            playlist_track["listener_id"],
            playlist_track["playlist_id"]
        )

    @allure.story("Get list of playlist tracks without playlist_id")
    def test_list_without_playlist_id(self, playlist_track_service):
        """GET /playlist-tracks - without playlist_id arg,should return 400 with  a list of tracks
        a message"""

        response = playlist_track_service.list()

        self.using(response).assert_status_code_is(StatusCodes.BAD_REQUEST)
        self.using(response).assert_response_has_key("message")


    @allure.story("Get playlist track by id")
    def test_get_by_id(self, listener_service, playlist_service, artist_service, album_service, track_service, playlist_track_service):
        """GET /playlist-tracks/<id> - should return 200 with  a track matching
        with ID.
        """
        #Create playlist_track via Factory
        factory = PlaylistTrackFactory(playlist_track_service, playlist_service, listener_service, artist_service, album_service, track_service)
        playlist_track = factory.create()
        playlist_track_id = playlist_track["id"]

        #GET by id
        get_response = playlist_track_service.get_by_id(playlist_track_id)

        self.using(get_response).assert_status_code_is(StatusCodes.OK)
        self.using(get_response).assert_response_has_key_value("id", playlist_track_id)

        #CLEANUP
        factory.cleanup(playlist_track_id)
        factory.cleanup_all(
            playlist_track["track_id"],
            playlist_track["album_id"],
            playlist_track["artist_id"],
            playlist_track["listener_id"],
            playlist_track["playlist_id"]
        )

    @allure.story("Get nonexistent playlist track ")
    def test_get_nonexistent_playlist_track(self, listener_service, playlist_service, artist_service, album_service, track_service, playlist_track_service):
        """GET /playlist-tracks/999999 - should return 404 with  a message.
        """

        response = playlist_track_service.get_by_id(999999)

        self.using(response).assert_status_code_is(StatusCodes.NOT_FOUND)
        self.using(response).assert_response_has_key("message")


@pytest.mark.playlist_track
@allure.feature("Playlist Tracks")
class TestPlaylistTrackUpdate(BaseAssertions):
    """Tests for PUT /playlist-tracks/<id> - """

    @allure.story("Update playlist track position field")
    def test_update_playlist_track_position(self, playlist_service, listener_service, artist_service, album_service, track_service, playlist_track_service):
        """PUT /playlist-tracks/<id> - should update only position field and return 200.
        Only the specific fields change; others remain untouched.
        """
        #Create playlist_track via Factory
        factory = PlaylistTrackFactory(playlist_track_service, playlist_service, listener_service, artist_service, album_service, track_service)
        playlist_track = factory.create()
        playlist_track_id = playlist_track["id"]

        service = playlist_track_service

        #Update position field
        update_payload = track_update_payload(position=5)
        update_response = service.update(playlist_track_id, update_payload)

        self.using(update_response).assert_status_code_is(StatusCodes.OK)
        self.using(update_response).assert_response_has_key_value("position", update_payload["position"])

        #CLEANUP
        factory.cleanup(playlist_track_id)
        factory.cleanup_all(
            playlist_track["track_id"],
            playlist_track["album_id"],
            playlist_track["artist_id"],
            playlist_track["listener_id"],
            playlist_track["playlist_id"]
        )


    @allure.story("Update playlist track track_id field")
    def test_playlist_track_invalid_update(self, playlist_service, listener_service, artist_service, album_service, track_service, playlist_track_service):
        """PUT /playlist-tracks/<id> - should return 400 with a message.
        """
        #Create playlist_track via Factory
        factory = PlaylistTrackFactory(playlist_track_service, playlist_service, listener_service, artist_service, album_service, track_service)
        playlist_track = factory.create()
        playlist_track_id = playlist_track["id"]

        service = playlist_track_service

        #Update track_id
        update_payload = track_update_payload(track_id=5)
        update_response = service.update(playlist_track_id, update_payload)

        self.using(update_response).assert_status_code_is(StatusCodes.BAD_REQUEST)
        self.using(update_response).assert_response_has_key("message")

        #CLEANUP
        factory.cleanup(playlist_track_id)
        factory.cleanup_all(
            playlist_track["track_id"],
            playlist_track["album_id"],
            playlist_track["artist_id"],
            playlist_track["listener_id"],
            playlist_track["playlist_id"]
        )

@pytest.mark.playlist_track
@allure.feature("Playlist Tracks")
class TestPlaylistTracksDelete(BaseAssertions):
    """Tests DELETE /playlist-tracks/<id>."""

    @allure.story("Delete playlist track successfully")
    def test_delete_success(self, playlist_service, listener_service, artist_service, album_service, track_service, playlist_track_service):
        """DELETE /playlist-tracks/<id> - should return 200 and delete permanently.
        """
        #Create playlist_track via Factory
        factory = PlaylistTrackFactory(playlist_track_service, playlist_service, listener_service, artist_service, album_service, track_service)
        playlist_track = factory.create()
        playlist_track_id = playlist_track["id"]

        service = playlist_track_service

        #delete
        delete_response = service.delete_playlist_track(playlist_track_id)

        self.using(delete_response).assert_status_code_is(StatusCodes.OK)
        self.using(delete_response).assert_response_has_key("message")

        #Check
        get_response = service.get_by_id(playlist_track_id)
        self.using(get_response).assert_status_code_is(StatusCodes.NOT_FOUND)

        #CLEANUP
        factory.cleanup_all(
            playlist_track["track_id"],
            playlist_track["album_id"],
            playlist_track["artist_id"],
            playlist_track["listener_id"],
            playlist_track["playlist_id"]
        )


    @allure.story("Delete nonexistent playlist track")
    def test_delete_nonexistent_playlist_track(self,  playlist_track_service):
        """DELETE /playlist-tracks/999999 - should return 404 and message.
        """
        response = playlist_track_service.delete_playlist_track(999999)

        self.using(response).assert_status_code_is(StatusCodes.NOT_FOUND)
        self.using(response).assert_response_has_key("message")


    @allure.story("Delete playlist track without auth")
    def test_delete_without_auth(self, playlist_service, listener_service, artist_service, album_service, track_service, playlist_track_service):
        """DELETE /playlist-tracks/<id> - should return 401 and delete permanently.
        """
        #Create playlist_track via Factory
        factory = PlaylistTrackFactory(playlist_track_service, playlist_service, listener_service, artist_service, album_service, track_service)
        playlist_track = factory.create()
        playlist_track_id = playlist_track["id"]

        #delete
        delete_service = PlaylistTrackService()
        delete_response = delete_service.delete_playlist_track(playlist_track_id)
        self.using(delete_response).assert_status_code_is(StatusCodes.UNAUTHORIZED)
        self.using(delete_response).assert_response_has_key("message")

        #CLEANUP
        factory.cleanup(playlist_track_id)
        factory.cleanup_all(
            playlist_track["track_id"],
            playlist_track["album_id"],
            playlist_track["artist_id"],
            playlist_track["listener_id"],
            playlist_track["playlist_id"]
        )

@pytest.mark.playlist_track
@allure.feature("Playlist Tracks")
class TestSideEffectsPlaylistTracks(BaseAssertions):
    """Business rules and side effects for Playlist Track operations."""

    @allure.story("autoincrement of position test")
    def test_create_playlist_auto_increment_position(self, playlist_service, listener_service, artist_service, album_service, track_service, playlist_track_service):
        """POST /playlist-tracks - all tracks added are incrementing position value.
        """
        #Create playlist_track 1 via Factory
        factory = PlaylistTrackFactory(playlist_track_service, playlist_service, listener_service, artist_service, album_service, track_service)
        playlist_track_1 = factory.create()
        playlist_track_id_1 = playlist_track_1["id"]
        playlist_id = playlist_track_1["playlist_id"]

        #Create playlist_track 2 via Factory
        playlist_track_2 = factory.create(playlist_id=playlist_id)
        playlist_track_id_2 = playlist_track_2["id"]
        position_2 = playlist_track_2["position"]

        assert position_2 == 2

        #CLEANUP
        #playlist track 1 and track 1 cascade
        factory.cleanup(playlist_track_id_1)
        factory.cleanup_track_cascade(playlist_track_1["track_id"], playlist_track_1["album_id"], playlist_track_1["artist_id"])

        #playlist track 2 and track 2 cascade
        factory.cleanup(playlist_track_id_2)
        factory.cleanup_track_cascade(playlist_track_2["track_id"], playlist_track_2["album_id"], playlist_track_2["artist_id"])

        #playlist cascade
        factory.cleanup_playlist_cascade(playlist_track_1["listener_id"], playlist_track_1["playlist_id"])


    @allure.story("adding track, update track_count")
    def test_adding_track_update_track_count(self, playlist_service, listener_service, artist_service, album_service, track_service, playlist_track_service):
        """POST /playlist-tracks - add a new track increases track_count value.
        """
        #Create playlist_track 1 via Factory
        factory = PlaylistTrackFactory(playlist_track_service, playlist_service, listener_service, artist_service, album_service, track_service)
        playlist_track_1 = factory.create()
        playlist_track_id_1 = playlist_track_1["id"]
        playlist_id = playlist_track_1["playlist_id"]

        response = playlist_service.get_by_id(playlist_id)
        data = response.json()

        #Create playlist_track 2 via Factory
        playlist_track_2 = factory.create(playlist_id=playlist_id)
        playlist_track_id_2 = playlist_track_2["id"]
        position_2 = playlist_track_2["position"]

        response_2 = playlist_service.get_by_id(playlist_id)
        data_2 = response_2.json()

        assert data["id"] == data_2["id"]
        assert data["track_count"] != data_2["track_count"]
        assert data_2["track_count"] == data["track_count"] + 1


        #CLEANUP
        #playlist track 1 and track 1 cascade
        factory.cleanup(playlist_track_id_1)
        factory.cleanup_track_cascade(playlist_track_1["track_id"], playlist_track_1["album_id"], playlist_track_1["artist_id"])

        #playlist track 2 and track 2 cascade
        factory.cleanup(playlist_track_id_2)
        factory.cleanup_track_cascade(playlist_track_2["track_id"], playlist_track_2["album_id"], playlist_track_2["artist_id"])

        #playlist cascade
        factory.cleanup_playlist_cascade(playlist_track_1["listener_id"], playlist_track_1["playlist_id"])


    @allure.story("removing track, update track_count")
    def test_removing_track_update_track_count(self, playlist_service, listener_service, artist_service, album_service, track_service, playlist_track_service):
        """POST /playlist-tracks - removing track decreases track_count value.
        """
        #Create playlist_track 1 via Factory
        factory = PlaylistTrackFactory(playlist_track_service, playlist_service, listener_service, artist_service, album_service, track_service)
        playlist_track = factory.create()
        playlist_track_id = playlist_track["id"]
        playlist_id = playlist_track["playlist_id"]

        response = playlist_service.get_by_id(playlist_id)
        data = response.json()

        #Eliminate track
        playlist_track_service.delete_playlist_track(playlist_track_id)

        response_2 = playlist_service.get_by_id(playlist_id)
        data_2 = response_2.json()

        assert data["id"] == data_2["id"]
        assert data["track_count"] != data_2["track_count"]
        assert data_2["track_count"] == data["track_count"] - 1


        #CLEANUP
        factory.cleanup_all(
            playlist_track["track_id"],
            playlist_track["album_id"],
            playlist_track["artist_id"],
            playlist_track["listener_id"],
            playlist_track["playlist_id"]
        )


    @allure.story("removing track, update update_at")
    def test_removing_track_time_stamp(self, playlist_service, listener_service, artist_service, album_service, track_service, playlist_track_service):
        """POST /playlist-tracks - removing track update updated_at value.
        """
        #Create playlist_track 1 via Factory
        factory = PlaylistTrackFactory(playlist_track_service, playlist_service, listener_service, artist_service, album_service, track_service)
        playlist_track = factory.create()
        playlist_track_id = playlist_track["id"]
        playlist_id = playlist_track["playlist_id"]

        response = playlist_service.get_by_id(playlist_id)
        data = response.json()

        #Eliminate track
        playlist_track_service.delete_playlist_track(playlist_track_id)

        response_2 = playlist_service.get_by_id(playlist_id)
        data_2 = response_2.json()

        assert data["id"] == data_2["id"]
        assert data_2["updated_at"] > data["updated_at"]

        #CLEANUP
        factory.cleanup_all(
            playlist_track["track_id"],
            playlist_track["album_id"],
            playlist_track["artist_id"],
            playlist_track["listener_id"],
            playlist_track["playlist_id"]
        )