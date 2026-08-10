"""Test for Artist API."""

import allure
import pytest

from tests.base.base_assertions import BaseAssertions
from tests.payloads.artist_payload import artist_create_payload, artist_update_payload, artist_login_payload
from tests.schemas.artist_schemas import ARTIST_RESPONSE_SCHEMA, ARTIST_LIST_SCHEMA
from tests.factories.artist_factory import ArtistFactory
from tests.utils.constants import StatusCodes, MusicGenres
from tests.utils.logger import get_logger

logger = get_logger(__name__)

@pytest.mark.artist
@allure.feature("Artists")
class TestArtistCreation(BaseAssertions):
    """Test for POST /artists - artist registration.

    Validates that the artist creation endpoint correctly handles
    valid input, missing fields valid data, and duplicate emails.
    """

    @allure.story("Create an Artist Successfully")
    @pytest.mark.smoke
    def test_create_artist_success(self, artist_service):
        """POST /artists - with all valid required fields should return 201
        and a response matching the ArtistResponse schema without password."""

        service = artist_service
        payload = artist_create_payload()

        response = service.create(payload)
        data = response.json()

        self.using(response).assert_status_code_is(StatusCodes.CREATED)
        self.using(response).assert_response_has_key("id")
        self.using(response).assert_response_key_absent("password")
        self.using(response).assert_response_key_absent("password_hash")
        self.using(response).assert_schema(ARTIST_RESPONSE_SCHEMA)
        self.using(response).assert_response_has_key_value("email", payload["email"])
        self.using(response).assert_response_has_key_value("genre_id", payload["genre_id"])

        #CLEANUP
        clean_response = service.delete_artist(data["id"])
        assert clean_response.status_code == StatusCodes.OK


    @allure.story("Create artist with missing required fields.")
    def test_create_artist_missing_fields(self, artist_service):
        """POST /artists with empty body should return 400
        with a message indicating which fields are missing.
        """
        service = artist_service
        response = service.create({})

        self.using(response).assert_status_code_is(StatusCodes.BAD_REQUEST)
        self.using(response).assert_response_has_key("message")


    @allure.story("Create artist with invalid email format.")
    def test_create_artist_invalid_email(self, artist_service):
        """POST /atirts - with invalid email format, should return 400
        with a message. The API validates email format before attempting BD insertion.
        """

        service = artist_service
        payload = artist_create_payload(email="is_not_email")

        response = service.create(payload)

        self.using(response).assert_status_code_is(StatusCodes.BAD_REQUEST)
        self.using(response).assert_response_has_key("message")


    @allure.story("Create artist with empty required fields")
    @pytest.mark.parametrize("field", ["stage_name", "first_name", "last_name", "email", "password"])
    def test_create_artist_empty_required_fields(self, artist_service, field):
        """POST /artists - with empty required fields should return 400,
        with message.
        """
        service = artist_service
        payload = artist_create_payload()
        payload[field] = ""

        response = service.create(payload)

        self.using(response).assert_status_code_is(StatusCodes.BAD_REQUEST)
        self.using(response).assert_response_has_key("message")


    @allure.story("Create artist with empty not required fields")
    @pytest.mark.parametrize("field", ["bio", "country"])
    def test_create_artist_empty_not_required_fields(self, artist_service, field):
        """POST /artists - with empty not required fields should return 201,
        and response matching with ArtistResponse schema.
        """
        service = artist_service
        payload = artist_create_payload()
        payload[field] = ""

        response = service.create(payload)
        data = response.json()
        logger.info("DATA data=%s", data)

        self.using(response).assert_status_code_is(StatusCodes.CREATED)
        self.using(response).assert_response_has_key("id")
        self.using(response).assert_schema(ARTIST_RESPONSE_SCHEMA)
        self.using(response).assert_response_has_key_value("stage_name", payload["stage_name"])

        #CLEANUP
        clean_response = service.delete_artist(data["id"])
        assert clean_response.status_code == StatusCodes.OK


    @allure.story("Create artist with long stage_name")
    def test_create_artist_long_stage_name(self, artist_service):
        """POST /artists - with long stage_name should return 400,
        and message.
        """
        service  = artist_service
        payload = artist_create_payload(stage_name="a" * 101)

        response = service.create(payload)

        self.using(response).assert_status_code_is(StatusCodes.BAD_REQUEST)
        self.using(response).assert_response_has_key("message")


    @allure.story("create artist with long bio")
    def test_create_artist_long_bio(self, artist_service):
        """POST /artists - with long bio should return 400,
        and message.
        """
        service = artist_service
        payload = artist_create_payload(bio= "a" * 501)

        response = service.create(payload)

        self.using(response).assert_status_code_is(StatusCodes.BAD_REQUEST)
        self.using(response).assert_response_has_key("message")


    @allure.story("Create artist with short password")
    def test_create_artist_short_password(self, artist_service):
        """POST /artists - with short password should return 400,
        and message.
        """
        service = artist_service
        payload = artist_create_payload(password="123")

        response = service.create(payload)

        self.using(response).assert_status_code_is(StatusCodes.BAD_REQUEST)
        self.using(response).assert_response_has_key("message")


    @allure.story("Create artist with non-existent genre_id")
    def test_create_artist_non_existent_genre_id(self, artist_service):
        """POST /artists - with non-existent genre_id, should return 400,
        and message.
        """
        service = artist_service
        payload = artist_create_payload(genre_id= 999999)

        response = service.create(payload)

        self.using(response).assert_status_code_is(StatusCodes.NOT_FOUND)
        self.using(response).assert_response_has_key("message")


    @allure.story("Create artist ignores read-only total_earnings")
    def test_create_artist_ignores_read_only_total_earnings(self, artist_service):
        """POST /artists - should ignore client-provided total_earnings
        and initialize it to 0.00.
        """
        service  = artist_service
        payload = artist_create_payload(total_earnings=-5)

        response = service.create(payload)
        data = response.json()

        self.using(response).assert_status_code_is(StatusCodes.CREATED)
        self.using(response).assert_response_has_key_value("total_earnings", 0.00)

        #CLEANUP
        clean_response = service.delete_artist(data["id"])
        assert  clean_response.status_code == StatusCodes.OK


@pytest.mark.artist
@allure.feature("Artists")
class TestArtistsRetrieval(BaseAssertions):
    """Test for GET /artists - GET /artists/<id> - GET /artists?genre_id="""

    @allure.story("Get artists list")
    def test_get_list(self, artist_service):
        """GET /artists - should return 200, with list of all artists."""

        response = artist_service.list()
        data = response.json()
        logger.info("DATA %s", data)

        self.using(response).assert_status_code_is(StatusCodes.OK)
        self.using(response).assert_schema(ARTIST_LIST_SCHEMA)


    @allure.story("Get artists list filtered by genre_id")
    def test_get_list_filtered_by_genre_id(self, artist_service):
        """GET /artists?genre_id= - should return 200 with a list of artists filtered by genre_id"""

        genre_id = MusicGenres.HIP_HOP
        response = artist_service.list(genre_id=genre_id)
        data = response.json()
        logger.info("GET DATA %s", data)

        self.using(response).assert_status_code_is(StatusCodes.OK)
        self.using(response).assert_schema(ARTIST_LIST_SCHEMA)
        assert all(artist["genre_id"] == genre_id for artist in data)


    @allure.story("Get artist by ID")
    def test_get_by_id(self, artist_service):
        """GET /artists/<id> - should return 200, and an artist matching with id."""

        #create artist
        service = artist_service
        payload = artist_create_payload()

        response = service.create(payload)
        data = response.json()
        artist_id = data["id"]
        self.using(response).assert_status_code_is(StatusCodes.CREATED)

        #get artists by id

        get_response = service.get_by_id(data["id"])
        get_data = get_response.json()
        logger.info("GET DATA %s", get_data)

        self.using(get_response).assert_status_code_is(StatusCodes.OK)
        self.using(response).assert_response_has_key_value("id", artist_id)
        self.using(response).assert_schema(ARTIST_RESPONSE_SCHEMA)

        #CLEAN UP
        clean_response = service.delete_artist(artist_id)
        assert clean_response.status_code == StatusCodes.OK

    @allure.story("Get non-existent artist")
    def test_get_non_existent_artist(self, artist_service):
        """GET /artists/999999 - should return 400, and message"""

        service = artist_service

        response = service.get_by_id(999999)

        self.using(response).assert_status_code_is(StatusCodes.NOT_FOUND)
        self.using(response).assert_response_has_key("message")
        self.using(response).assert_response_key_absent("password")
        self.using(response).assert_response_key_absent("password_hash")

@pytest.mark.artist
@allure.feature("Artists")
class TestsUpdateArtist(BaseAssertions):
    """PUT /artists/<id>"""

    @allure.story("Update data successfully")
    def test_update_success(self, artist_service):
        """PUT /artists/<id> - should update the provided fields and return 200.
        Only the specific fields change; others remain untouched.
        """
        artist = ArtistFactory(artist_service).create()
        service = artist_service

        #update fields
        update_payload = artist_update_payload(
            stage_name="Slim Shady",
            first_name="Marshall Bruce",
            last_name="Mathers III",
            bio=("Grammy-winning rapper, producer, and songwriter. "
                "Known for his alter ego Slim Shady and lyrical storytelling.")
        )
        update_response = service.update(artist["id"],update_payload)

        self.using(update_response).assert_status_code_is(StatusCodes.OK)
        self.using(update_response).assert_response_has_key_value("id", artist["id"])
        self.using(update_response).assert_response_has_key_value("first_name", update_payload["first_name"])
        self.using(update_response).assert_response_has_key_value("last_name", update_payload["last_name"])
        self.using(update_response).assert_response_has_key_value("country", artist["country"])

        #CLEANUP
        service.delete_artist(artist["id"])


    @allure.story("Update data timestamp")
    def test_update_timestamp(self, artist_service):
        """PUT /artists/<id> - should update the provided fields and return 200.
        Updated_at must change.
        """
        artist = ArtistFactory(artist_service).create()
        service = artist_service

        #update fields
        update_payload = artist_update_payload(stage_name="Slim Shady")
        update_response = service.update(artist["id"],update_payload)
        update_data = update_response.json()

        self.using(update_response).assert_status_code_is(StatusCodes.OK)
        self.using(update_response).assert_response_has_key_value("id", artist["id"])
        assert update_data["updated_at"] > artist["updated_at"]

        #CLEANUP
        service.delete_artist(artist["id"])


    @allure.story("Update read-only field total_earnings")
    def test_artist_total_earnings_cannot_be_updated_directly(self, artist_service):
        """PUT /artists/<id> - attempting to update read-only field
        total_earnings, should be return 400 and message.
        """
        artist = ArtistFactory(artist_service).create()
        service = artist_service

        #update fields
        update_payload = artist_update_payload(total_earnings= 999.99)
        update_response = service.update(artist["id"],update_payload)

        self.using(update_response).assert_status_code_is(StatusCodes.BAD_REQUEST)
        self.using(update_response).assert_response_has_key_value("total_earnings", None)

        #CLEANUP
        service.delete_artist(artist["id"])


    @allure.story("Update non-existent artists")
    def test_update_non_existent_artist(self, artist_service):
        """PUT /artists/999999 -  should be return 404 and message.
        """

        update_payload = artist_update_payload(stage_name="Slim Shady")
        update_response = artist_service.update(999999,update_payload)

        self.using(update_response).assert_status_code_is(StatusCodes.NOT_FOUND)
        self.using(update_response).assert_response_has_key("message")



@allure.feature("Artists")
class TestDeleteArtist(BaseAssertions):
    """Test for DELETE /artists/<id>."""

    @allure.story("Delete artist successfully.")
    def test_artist_delete_success(self, artist_service):
        """DELETE /artists/<id> - should return 200 for artist
        with not active album and not pending royalty.
        """
        artist = ArtistFactory(artist_service).create()
        service = artist_service

        #delete artist
        del_response = service.delete_artist(artist["id"])
        self.using(del_response).assert_status_code_is(StatusCodes.OK)
        self.using(del_response).assert_response_has_key("message")

        #check the artist is totally eliminate
        get_response = service.get_by_id(artist["id"])
        self.using(get_response).assert_status_code_is(StatusCodes.NOT_FOUND)
        self.using(get_response).assert_response_has_key("message")


    @allure.story("Delete non-existent artist")
    def test_delete_non_existent_artist(self, artist_service):
        """DELETE /artists/999999 - should return 404 and message."""

        response = artist_service.delete_artist(999999)

        self.using(response).assert_status_code_is(StatusCodes.NOT_FOUND)
        self.using(response).assert_response_has_key("message")


@pytest.mark.artist
@allure.feature("Artists")
class TestArtistAuth(BaseAssertions):
    """Tests for /artists/login."""

    @allure.story("Login Artist successfully")
    def test_login_success(self, artist_service):
        """POST /artists/login - with correct email/password should return 200.
        With a JWT in the response body.
        """
        service = artist_service
        payload = artist_login_payload("artist@beatflow.com","Artist123!")

        response = service.login(payload)
        data = response.json()

        self.using(response).assert_status_code_is(StatusCodes.OK)
        self.using(response).assert_response_has_key("message")
        self.using(response).assert_response_has_key("token")


    @allure.story("Login artist missing fields")
    def test_login_missing_field(self, artist_service):
        """POST /artists/login - with empty should return 400
        and message.
        """
        service = artist_service
        response = service.login({})

        self.using(response).assert_status_code_is(StatusCodes.BAD_REQUEST)
        self.using(response).assert_response_has_key("message")


    @allure.story("Login artist wrong credentials")
    def test_login_wrong_pass(self, artist_service):
        """POST /artists/login - with wrong password should return 400
        and message.
        """

        service = artist_service
        payload = artist_login_payload("artist@beatflow.com","12345678")

        response = service.login(payload)

        self.using(response).assert_status_code_is(StatusCodes.UNAUTHORIZED)
        self.using(response).assert_response_has_key("message")




