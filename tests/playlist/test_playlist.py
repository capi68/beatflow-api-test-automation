"""Test for Playlist API."""

import allure
import pytest
from pip._internal.resolution.resolvelib import factory

from tests.base.base_assertions import BaseAssertions
from tests.services.playlist_service import PlaylistService
from tests.payloads.playlist_payload import playlist_create_payload, playlist_update_payload
from tests.schemas.playlist_schemas import PLAYLIST_RESPONSE_SCHEMA, PLAYLIST_LIST_SCHEMA
from tests.factories.listener_factory import ListenerFactory
from tests.factories.playlist_factory import PlaylistFactory
from tests.factories.playlist_track_factory import PlaylistTrackFactory
from tests.utils.constants import StatusCodes
from tests.utils.logger import get_logger

logger = get_logger(__name__)

@pytest.mark.playlist
@allure.feature("Playlists")
class TestCreatePlaylist(BaseAssertions):
    """Tests for POST /playlists - playlists registration,
    validates that the playlist creation endpoint correctly handles,
    valid input, missing fields, valid data.
    """

    @allure.story("Create playlist successfully")
    def test_create_playlist_success(self, listener_service, playlist_service):
        """POST /playlists - with valid data required fields should return 201;
        and response matching with Playlist Response Schema.
        """
        #create listener via factory
        factory = ListenerFactory(listener_service)
        listener = factory.create()
        listener_id = listener["id"]

        service = playlist_service

        #create playlist
        payload = playlist_create_payload(listener_id=listener_id)
        response = service.create(payload)
        data = response.json()

        self.using(response).assert_status_code_is(StatusCodes.CREATED)
        self.using(response).assert_response_has_key("id")
        self.using(response).assert_schema(PLAYLIST_RESPONSE_SCHEMA)
        self.using(response).assert_response_has_key_value("name", payload["name"])

        #CLEANUP
        clean_response = service.delete_playlist(data["id"])
        assert clean_response.status_code == StatusCodes.OK

        factory.cleanup(listener_id)


    @allure.story("Exceed max number of playlist per listener")
    def test_exceed_maximum_playlist_per_listener(self, listener_service, playlist_service):
        """POST /playlist - Exceed max number playlist per listener (50),
        should return 400 with message.
        """
        #create a listener via Factory
        factory = ListenerFactory(listener_service)
        listener = factory.create()
        listener_id = listener["id"]

        #create previous 50 playlist via API
        playlist_factory = PlaylistFactory(listener_service, playlist_service)

        playlist_ids = []
        for i in range(50):
            playlist = playlist_factory.create(listener_id=listener_id, name=f"Playlist{i}")

            playlist_ids.append(playlist["id"])

        #create playlist 51
        service = playlist_service
        payload = playlist_create_payload(listener_id=listener_id, name="Playlist 51")
        response = service.create(payload)

        self.using(response).assert_status_code_is(StatusCodes.BAD_REQUEST)
        self.using(response).assert_response_has_key("message")

        #CLEANUP
        for playlist_id in playlist_ids:
            playlist_factory.cleanup(playlist_id)
        factory.cleanup(listener_id)


    @allure.story("Create playlist with nonexistent listener")
    def test_create_playlist_non_existent_listener(self, listener_service, playlist_service):
        """POST /playlists - with nonexistent listener, should return 404,
        with message.
        """
        service = playlist_service

        #create playlist
        payload = playlist_create_payload(listener_id=999999)
        response = service.create(payload)

        self.using(response).assert_status_code_is(StatusCodes.NOT_FOUND)
        self.using(response).assert_response_has_key("message")


    @allure.story("Create playlist name boundary values.")
    @pytest.mark.parametrize("value", ["", "a" * 201])
    def test_create_playlist_name_boundary_values(self, listener_service, playlist_service, value):
        """POST /playlists - with name boundary values, should return 400,
        with message.
        """
        #create listener via factory
        factory = ListenerFactory(listener_service)
        listener = factory.create()
        listener_id = listener["id"]

        service = playlist_service

        #create playlist
        payload = playlist_create_payload(listener_id=listener_id, name=value)
        response = service.create(payload)
        data = response.json()

        self.using(response).assert_status_code_is(StatusCodes.BAD_REQUEST)
        self.using(response).assert_response_has_key("message")

        #CLEANUP
        factory.cleanup(listener_id)



    @allure.story("Create playlist description boundary values.")
    def test_create_playlist_description_boundary_values(self, listener_service, playlist_service):
        """POST /playlists - with description boundary values, should return 400,
        with message.
        """
        #create listener via factory
        factory = ListenerFactory(listener_service)
        listener = factory.create()
        listener_id = listener["id"]

        service = playlist_service

        #create playlist
        payload = playlist_create_payload(listener_id=listener_id, description="a" * 501)
        response = service.create(payload)
        data = response.json()

        self.using(response).assert_status_code_is(StatusCodes.BAD_REQUEST)
        self.using(response).assert_response_has_key("message")

        #CLEANUP
        factory.cleanup(listener_id)



    @allure.story("Create playlist without description.")
    def test_create_playlist_whit_out_description(self, listener_service, playlist_service):
        """POST /playlists - without description, should return 201,
        and create playlist.
        """
        #create listener via factory
        factory = ListenerFactory(listener_service)
        listener = factory.create()
        listener_id = listener["id"]

        service = playlist_service

        #create playlist
        payload = playlist_create_payload(listener_id=listener_id, description=None)
        response = service.create(payload)
        data = response.json()

        self.using(response).assert_status_code_is(StatusCodes.CREATED)
        self.using(response).assert_response_has_key("id")


        #CLEANUP
        clean_response = service.delete_playlist(data["id"])
        assert  clean_response.status_code == StatusCodes.OK

        factory.cleanup(listener_id)



    @allure.story("Create playlist track_count start at zero")
    def test_create_playlist_track_count_start_zero(self, listener_service, playlist_service):
        """POST /playlists - with valid data required fields should return 201;
        and track_count start at zero.
        """
        #create listener via factory
        factory = ListenerFactory(listener_service)
        listener = factory.create()
        listener_id = listener["id"]

        service = playlist_service

        #create playlist
        payload = playlist_create_payload(listener_id=listener_id)
        response = service.create(payload)
        data = response.json()

        self.using(response).assert_status_code_is(StatusCodes.CREATED)
        assert data["track_count"] == 0

        #CLEANUP
        clean_response = service.delete_playlist(data["id"])
        assert clean_response.status_code == StatusCodes.OK

        factory.cleanup(listener_id)



    @allure.story("Create playlist is_public default False")
    def test_create_playlist_is_public_default_false(self, listener_service, playlist_service):
        """POST /playlists - with valid data required fields should return 201;
        and is_public default False.
        """
        #create listener via factory
        factory = ListenerFactory(listener_service)
        listener = factory.create()
        listener_id = listener["id"]

        service = playlist_service

        #create playlist
        payload = playlist_create_payload(listener_id=listener_id)
        response = service.create(payload)
        data = response.json()

        self.using(response).assert_status_code_is(StatusCodes.CREATED)
        assert data["is_public"] == False

        #CLEANUP
        clean_response = service.delete_playlist(data["id"])
        assert clean_response.status_code == StatusCodes.OK

        factory.cleanup(listener_id)


@pytest.mark.playlist
@allure.feature("Playlist")
class TestPlaylistRetrieval(BaseAssertions):
    """Tests for GET /playlists - GET /playlists/<id>."""

    @allure.story("Get list of playlist")
    def test_playlist_list(self, playlist_service):
        """GET /playlists - get list of all active playlist."""

        response = playlist_service.list()

        self.using(response).assert_status_code_is(StatusCodes.OK)
        self.using(response).assert_schema(PLAYLIST_LIST_SCHEMA)


    @allure.story("Get list of playlist filtered by listener_id")
    def test_playlist_list_filtered_by_listener_id(self, playlist_service, listener_service):
        """GET /playlists - get list of all active playlist filtered by listener_id."""
        #Create playlist via Factory
        factory = PlaylistFactory(listener_service, playlist_service)
        playlist = factory.create()
        playlist_id = playlist["id"]
        listener_id = playlist["listener_id"]

        #Get list by listener_id
        response = playlist_service.list(listener_id)
        data = response.json()

        self.using(response).assert_status_code_is(StatusCodes.OK)
        assert all(playlist["listener_id"] == listener_id for playlist in data)

        #CLEANUP
        factory.cleanup(playlist_id)
        factory.cleanup_all(listener_id)


    @allure.story("Get list of playlist filtered by is_public")
    def test_playlist_list_filtered_by_is_public(self, playlist_service, listener_service):
        """GET /playlists - should return 200 and list of all active playlist filtered by is_public."""
        #Create playlist via Factory
        factory = PlaylistFactory(listener_service, playlist_service)
        playlist = factory.create()
        playlist_id = playlist["id"]
        listener_id = playlist["listener_id"]
        update_response = playlist_service.update(playlist_id, {"is_public": True})

        #Get list by listener_id
        response = playlist_service.list(is_public=True)
        data = response.json()

        self.using(response).assert_status_code_is(StatusCodes.OK)
        assert all(playlist["is_public"] == True for playlist in data)

        #CLEANUP
        factory.cleanup(playlist_id)
        factory.cleanup_all(listener_id)


    @allure.story("Get playlist by id")
    def test_get_by_id(self, playlist_track_service, playlist_service, listener_service,artist_service, album_service, track_service):
        """GET /playlists/<id> - should return 200 and get playlist by ID. includes track."""
        #Create playlist via Factory
        factory = PlaylistTrackFactory(playlist_track_service, playlist_service, listener_service,artist_service, album_service, track_service)
        playlist_track = factory.create()
        playlist_track_id = playlist_track["id"]

        #Get list by listener_id
        response = playlist_service.get_by_id(playlist_track["playlist_id"])

        self.using(response).assert_status_code_is(StatusCodes.OK)
        self.using(response).assert_response_has_key_value("id", playlist_track["playlist_id"])
        self.using(response).assert_response_has_key("tracks")

        #CLEANUP
        factory.cleanup(playlist_track_id)
        factory.cleanup_all(
            playlist_track["track_id"],
            playlist_track["album_id"],
            playlist_track["artist_id"],
            playlist_track["listener_id"],
            playlist_track["playlist_id"]
        )

    @allure.story("Get nonexistent playlist")
    def test_get_nonexistent_playlist(self,playlist_service):
        """GET /playlists/999999 - should return 404 and message"""

        response = playlist_service.get_by_id(9999999)

        self.using(response).assert_status_code_is(StatusCodes.NOT_FOUND)
        self.using(response).assert_response_has_key("message")


@pytest.mark.playlist
@allure.feature("Playlist")
class TestUpdatePlaylist(BaseAssertions):
    """Tests for PUT /playlist/<id>."""

    @allure.story("Update playlist success.")
    def test_update_success(self, listener_service, playlist_service):
        """PUT /playlists/<id> - should return 200 and update provided fields data, other remains."""
        #create playlist via Factory
        factory = PlaylistFactory(listener_service, playlist_service)
        playlist = factory.create()
        playlist_id = playlist["id"]

        response = playlist_service.update(
            playlist_id,
            {"name": "Update name", "description": "description update", "is_public": True}
            )

        self.using(response).assert_status_code_is(StatusCodes.OK)
        self.using(response).assert_response_has_key_value("name", "Update name")
        self.using(response).assert_response_has_key_value("description", "description update")
        self.using(response).assert_response_has_key_value("is_public", True)
        self.using(response).assert_response_has_key_value("listener_id", playlist["listener_id"])

        #CLEANUP
        factory.cleanup(playlist_id)
        factory.cleanup_all(playlist["listener_id"])


    @allure.story("Update nonexistent playlist.")
    def test_update_nonexistent_playlist(self, listener_service, playlist_service):
        """PUT /playlists/999999 - should return 400 and message."""

        response = playlist_service.update(999999,{"name": "Update name"}
        )

        self.using(response).assert_status_code_is(StatusCodes.NOT_FOUND)
        self.using(response).assert_response_has_key("message")


@pytest.mark.playlist
@allure.feature("Playlist")
class TestDeletePlaylist(BaseAssertions):
    """Test for DELETE /playlist/<id>."""

    @allure.story("DELETE playlist success.")
    def test_delete_success(self, playlist_service, listener_service):
        """DELETE /playlists/<id> - should return 200 and message."""
        #Create playlist by Factory
        factory = PlaylistFactory(listener_service, playlist_service)
        playlist=factory.create()
        playlist_id =playlist["id"]

        response = playlist_service.delete_playlist(playlist_id)

        self.using(response).assert_status_code_is(StatusCodes.OK)
        self.using(response).assert_response_has_key("message")

        #CLEANUP
        factory.cleanup_all(playlist["listener_id"])


    @allure.story("DELETE nonexistent playlist.")
    def test_delete_nonexistent_playlist(self, playlist_service, listener_service):
        """DELETE /playlists/999999 - should return 400 and message."""

        response = playlist_service.delete_playlist(999999)

        self.using(response).assert_status_code_is(StatusCodes.NOT_FOUND)
        self.using(response).assert_response_has_key("message")


