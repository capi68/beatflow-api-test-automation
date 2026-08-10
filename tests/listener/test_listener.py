"""Test for  Listener API."""

import allure
import pytest
from datetime import date

from tests.base.base_assertions import BaseAssertions
from tests.services.listener_service import ListenerService
from tests.payloads.listener_payload import listener_create_payload, listener_update_payload, listener_login_payload
from tests.schemas.listener_schemas import LISTENER_RESPONSE_SCHEMA, LISTENER_LIST_SCHEMA, LISTENER_LOGIN_RESPONSE_SCHEMA
from tests.factories.subscription_factory import SubscriptionFactory
from tests.utils.logger import get_logger
from tests.utils.constants import StatusCodes

logger = get_logger(__name__)

@pytest.mark.listener
@allure.feature("Listeners")
class TestCreateListener(BaseAssertions):
    """Tests for POST /listeners - listener registration
    Validates that the listener creation endpoint correctly handles
    valid input, missing fields, valid data, and duplicate emails.
    """

    @allure.story("Create a listener successfully")
    @pytest.mark.smoke
    def test_create_listener_success(self, listener_service):
        """POST /listeners with a valid required fields should return 201;
        and a response matching the ListenerResponse schema without password.
        """
        service = listener_service

        payload = listener_create_payload()
        response = service.create(payload)
        data = response.json()

        self.using(response).assert_status_code_is(StatusCodes.CREATED)
        self.using(response).assert_response_has_key("id")
        self.using(response).assert_response_key_absent("password")
        self.using(response).assert_response_key_absent("password_hash")
        self.using(response).assert_schema(LISTENER_RESPONSE_SCHEMA)
        self.using(response).assert_response_has_key_value("username", payload["username"])

        #CLEANUP
        clean_response =service.delete_listener(data["id"])
        assert clean_response.status_code == StatusCodes.OK


    @allure.story("Create listener with missing required fields")
    def test_create_listener_missing_fields(self, listener_service):
        """POST /listeners with empty body should return 400.
        with message.
        """

        service = listener_service

        response = service.create({})

        self.using(response).assert_status_code_is(StatusCodes.BAD_REQUEST)
        self.using(response).assert_response_has_key("message")


    @allure.story("Create listener with invalid email")
    def test_create_listener_invalid_email(self, listener_service):
        """POST /listener - with invalid email should return 400.
        with message. The PAI validates email before attempting DB insertion.
        """

        service = listener_service
        payload = listener_create_payload(email="not-an-email")

        response = service.create(payload)

        self.using(response).assert_status_code_is(StatusCodes.BAD_REQUEST)
        self.using(response).assert_response_has_key("message")


    @pytest.mark.parametrize("field", ["username", "email", "password", "first_name", "last_name"])
    @allure.story("Create listener with empty required fields")
    def test_create_listener_empty_required_fields(self, listener_service, field):
        """POST /listener - with empty required fields return 400.
        with message indicating which field are empty.
        """

        service = listener_service
        payload = listener_create_payload(**{field: ""})

        response = service.create(payload)

        self.using(response).assert_status_code_is(StatusCodes.BAD_REQUEST)
        self.using(response).assert_response_has_key("message")


    @pytest.mark.parametrize("field", ["username", "email", "password", "first_name", "last_name"])
    @allure.story("Create listener with invalid data type")
    def test_create_listener_invalid_fields_type(self, listener_service, field):
        """POST /listener - with invalid data type should return 400.
        with message indicating which field are empty.
        """

        service = listener_service
        payload = listener_create_payload(**{field: 1})

        response = service.create(payload)

        self.using(response).assert_status_code_is(StatusCodes.BAD_REQUEST)
        self.using(response).assert_response_has_key("message")


    @allure.story("Create listener with short password")
    def test_create_listener_short_password(self, listener_service):
        """POST /listeners - with short password should return 400.
        with message.
        """
        service = listener_service
        payload = listener_create_payload(password="1234567")

        response = service.create(payload)

        self.using(response).assert_status_code_is(StatusCodes.BAD_REQUEST)
        self.using(response).assert_response_has_key("message")


    @allure.story("Create listener with duplicate email")
    def test_create_listener_duplicate_email(self, listener_service):
        """POST /listeners - with duplicate email should return 409
        with message.
        """
        service = listener_service
        payload = listener_create_payload()
        email = payload["email"]

        #first create
        response = service.create(payload)
        self.using(response).assert_status_code_is(StatusCodes.CREATED)
        data =response.json()

        #second create
        payload_2 = listener_create_payload(email=email)
        response_2 = service.create(payload_2)

        self.using(response_2).assert_status_code_is(StatusCodes.CONFLICT)
        self.using(response_2).assert_response_has_key("message")

        #CLEANUP
        listener_service.delete_listener(data["id"])

    @pytest.mark.parametrize("username", ["aa", "a" * 51])
    @allure.story("Create listener with username out of range")
    def test_create_listener_username_out_of_range(self, listener_service, username):
        """POST /listeners - with username out of range, should return 400;
        with message.
        """
        service  = listener_service
        payload = listener_create_payload(username=username)

        response = service.create(payload)

        self.using(response).assert_status_code_is(StatusCodes.BAD_REQUEST)
        self.using(response).assert_response_has_key("message")


    @allure.story("Create listener with duplicate username")
    def test_create_listener_duplicate_username(self, listener_service):
        """POST /listeners - with duplicate username should return 409;
        with message.
        """

        service = listener_service
        payload = listener_create_payload()
        username = payload["username"]

        #First CREATE
        response = service.create(payload)
        self.using(response).assert_status_code_is(StatusCodes.CREATED)
        data = response.json()

        #Second create, same username
        payload_2 = listener_create_payload(username=username)
        response_2 = service.create(payload_2)

        self.using(response_2).assert_status_code_is(StatusCodes.CONFLICT)
        self.using(response_2).assert_response_has_key("message")

        #CLEANUP
        listener_service.delete_listener(data["id"])


    @allure.story("Create listener with wrong date_of_birth pattern.")
    def test_create_listener_wrong_pattern_date_of_birth(self, listener_service):
        """POST /listener - with wrong date_of_birth pattern
        should return 400 and message.
        """
        service = listener_service
        payload =listener_create_payload(date_of_birth="17-08-1992")

        response = service.create(payload)

        self.using(response).assert_status_code_is(StatusCodes.BAD_REQUEST)
        self.using(response).assert_response_has_key("message")


    @allure.story("Create listener under minimum age")
    def test_create_listener_under_minimum_age(self, listener_service):
        """POST /listener - create listener younger than 13 years old
        should return 400 and message.
        """
        #create a dynamic date_of_birth that always by 12 years old
        today = date.today()
        under_minimum_age = today.replace(year=today.year - 12)
        service = listener_service
        payload =listener_create_payload(date_of_birth=under_minimum_age.isoformat())

        response = service.create(payload)

        self.using(response).assert_status_code_is(StatusCodes.BAD_REQUEST)
        self.using(response).assert_response_has_key("message")


@pytest.mark.listener
@allure.feature("Listeners")
class TestListenerRetrieval(BaseAssertions):
    """Tests for GET /listeners - GET /listeners/<id> - """

    @allure.story("Get list of all listeners")
    def test_list_listeners(self, listener_service):
        """GET /listeners - should return 200 with a list of active listeners.
        ordered by username.
        """

        response = listener_service.list()
        data = response.json()
        logger.info("DATA: %s", data)

        usernames = [listener["username"] for listener in data]

        self.using(response).assert_status_code_is(StatusCodes.OK)
        self.using(response).assert_schema(LISTENER_LIST_SCHEMA)
        assert usernames == sorted(usernames)


    @allure.story("Get listener by id")
    def test_by_id(self, listener_service):
        """GET /listeners/<id> - should return 200 with listener matching with ID.
        """
        service = listener_service
        payload = listener_create_payload()

        response = service.create(payload)
        self.using(response).assert_status_code_is(StatusCodes.CREATED)
        data = response.json()

        #get by id
        get_response = service.get_by_id(data["id"])

        self.using(get_response).assert_status_code_is(StatusCodes.OK)
        self.using(get_response).assert_schema(LISTENER_RESPONSE_SCHEMA)
        self.using(get_response).assert_response_has_key_value("id", data["id"])

        #CLEANUP
        clean_response = service.delete_listener(data["id"])
        assert clean_response.status_code == StatusCodes.OK


    @allure.story("Get nonexistent listener")
    def test_non_existent_listener(self, listener_service):
        """GET /listeners/999999 - should return 400 with message.
        """
        response = listener_service.get_by_id(999999)
        data = response.json()

        self.using(response).assert_status_code_is(StatusCodes.NOT_FOUND)
        self.using(response).assert_response_has_key("message")


    @allure.story("Get list listeners without auth.")
    def test_list_listeners_unauthorized(self):
        """GET /listeners without Authorization header should return 401."""

        service = ListenerService() #no token

        response = service.list()

        self.using(response).assert_status_code_is(StatusCodes.UNAUTHORIZED)
        self.using(response).assert_response_has_key("message")


@pytest.mark.listener
@allure.feature("Listeners")
class TestUpdateListener(BaseAssertions):
    """PUT /listeners/<id>."""

    @allure.story("Update a listener successfully.")
    def test_update_listener_success(self, listener_service):
        """PUT /listeners/<id> - should update the provided fields and return 200.
        Only the specific fields change; others remain untouched.
        """
        service = listener_service
        payload = listener_create_payload()

        response = service.create(payload)
        data = response.json()
        self.using(response).assert_status_code_is(StatusCodes.CREATED)

        #update listener
        update_payload = listener_update_payload(
            first_name="Anna Maria",
            last_name="Santos Gomez",
            country="Canada",
        )
        update_service = service.update(data["id"], update_payload)

        self.using(update_service).assert_status_code_is(StatusCodes.OK)
        self.using(update_service).assert_response_has_key_value("id", data["id"])
        self.using(update_service).assert_response_has_key_value("first_name", update_payload["first_name"])
        self.using(update_service).assert_response_has_key_value("last_name", update_payload["last_name"])
        self.using(update_service).assert_response_key_absent("password")
        self.using(update_service).assert_response_key_absent("password_hash")

        #CLEANUP
        clean_response = service.delete_listener(data["id"])
        assert clean_response.status_code == StatusCodes.OK


    @pytest.mark.track
    @allure.story("Update listener date_of_birth not allowed")
    def test_update_listener_date_of_birth_not_allowed(self, listener_service):
        """PUT /listeners/<id> - date_of_birth is not allowed, should return 400
        with message.
        """
        service = listener_service
        payload = listener_create_payload()

        response = service.create(payload)
        data = response.json()
        self.using(response).assert_status_code_is(StatusCodes.CREATED)

        #update listener
        update_payload = listener_update_payload(date_of_birth="1993-08-17")
        update_service = service.update(data["id"], update_payload)

        self.using(update_service).assert_status_code_is(StatusCodes.BAD_REQUEST)

        #CLEANUP
        clean_response = service.delete_listener(data["id"])
        assert clean_response.status_code == StatusCodes.OK

    @allure.story("Update nonexistent listener.")
    def test_update_non_existent_listener(self, listener_service):
        """PUT /listeners/999999 - should return 404 with message."""

        payload = listener_update_payload(first_name="Maria")

        response = listener_service.update(999999, payload)

        self.using(response).assert_status_code_is(StatusCodes.NOT_FOUND)
        self.using(response).assert_response_has_key("message")

@pytest.mark.listener
@allure.feature("Listeners")
class TestDeleteListener(BaseAssertions):
    """Tests  DELETE /listeners/<id>."""

    @allure.story("Delete listener successfully")
    def test_delete_listener_success(self, listener_service):
        """DELETE /listeners/<id> - should return 200 and message."""

        #create listener
        service = listener_service
        payload = listener_create_payload()

        response = service.create(payload)
        data = response.json()
        self.using(response).assert_status_code_is(StatusCodes.CREATED)

        #delete listener
        del_response = service.delete_listener(data["id"])
        self.using(del_response).assert_status_code_is(StatusCodes.OK)
        self.using(del_response).assert_response_has_key("message")

        #confirm
        get_response = service.get_by_id(data["id"])
        self.using(get_response).assert_status_code_is(StatusCodes.NOT_FOUND)


    @allure.story("Delete nonexistent listener")
    def test_delete_nonexistent_listener(self, listener_service):
        """DELETE /listeners/999999 - should return 404 and message."""

        response = listener_service.delete_listener(999999)

        self.using(response).assert_status_code_is(StatusCodes.NOT_FOUND)
        self.using(response).assert_response_has_key("message")


    @allure.story("Delete listener with active subscription")
    def test_delete_listener_active_subscription(self, listener_service, subscription_service):
        """DELETE /listeners/<id> - with active subscription
        should return 409 and message.
        """
        #Create listener with active subscription via Factory
        subscription_factory = SubscriptionFactory(subscription_service, listener_service)
        listener_subscription = subscription_factory.create()
        subscription_id = listener_subscription["id"]
        listener_id = listener_subscription["listener_id"]

        response = listener_service.delete_listener(listener_id)

        self.using(response).assert_status_code_is(StatusCodes.CONFLICT)

        #CLEANUP
        subscription_service.update(subscription_id, {"status": "cancelled"})
        subscription_factory.cleanup_all(listener_id)


@pytest.mark.listener
@allure.feature("Listeners")
class TestLoginListener(BaseAssertions):
    """Tests POST /listeners/login."""

    @allure.story("Login listener success with valid credentials.")
    def test_login_success(self, listener_service):
        """POST /listeners/login with correct email/password should return 200;
        with JWT token in the response body.
        """
        payload = listener_login_payload("listener@beatflow.com","Listener123!")

        response = listener_service.login(payload)

        self.using(response).assert_status_code_is(StatusCodes.OK)
        self.using(response).assert_response_has_key("token")
        self.using(response).assert_response_has_key("message")
        self.using(response).assert_schema(LISTENER_LOGIN_RESPONSE_SCHEMA)


    @allure.story("Login listener wrong password.")
    def test_login_wrong_password(self, listener_service):
        """POST /listeners/login with wrong password should return 401;
        with message.
        """
        payload = listener_login_payload("listener@beatflow.com","Listener1234!")

        response = listener_service.login(payload)

        self.using(response).assert_status_code_is(StatusCodes.UNAUTHORIZED)
        self.using(response).assert_response_has_key("message")



    @allure.story("Login listener with missing fields.")
    def test_login_missing_fields(self, listener_service):
        """POST /listeners/login with empty body should return 400;
        with message.
        """

        response = listener_service.login({})

        self.using(response).assert_status_code_is(StatusCodes.BAD_REQUEST)
        self.using(response).assert_response_has_key("message")