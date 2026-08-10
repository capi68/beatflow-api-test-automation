"""Test for subscriptions API."""

import allure
import pytest

from datetime import datetime, timedelta
from tests.base.base_assertions import BaseAssertions
from tests.payloads.subscription_payload import subscription_create_payload, subscription_update_payload
from tests.schemas.subscription_schemas import SUBSCRIPTION_LIST_SCHEMA, SUBSCRIPTION_RESPONSE_SCHEMA
from tests.factories.listener_factory import ListenerFactory
from tests.utils.constants import StatusCodes
from tests.utils.logger import get_logger

logger = get_logger(__name__)

@pytest.mark.subscription
@allure.feature("Subscriptions")
class TestSubscriptionCreate(BaseAssertions):
    """Tests for POST /subscriptions - subscription registration.

    Validates that the album creation endpoint correctly handles
    valid input and missing fields.
    """

    @allure.story("Create subscription successfully")
    def test_create_subs_success(self, listener_service, subscription_service):
        """POST /subscriptions - with all required fields should return 201.
        and a response matching the Subscription Response schema.
        """
        #create listener via Factory
        factory = ListenerFactory(listener_service)
        listener = factory.create()
        listener_id = listener["id"]

        #create subscription
        service = subscription_service
        payload = subscription_create_payload(listener_id=listener_id)

        response = service.create(payload)
        data = response.json()

        self.using(response).assert_status_code_is(StatusCodes.CREATED)
        self.using(response).assert_response_has_key("id")
        self.using(response).assert_response_has_key_value("expires_at", None)
        self.using(response).assert_schema(SUBSCRIPTION_RESPONSE_SCHEMA)

        #CLEANUP
        clean_payload = subscription_update_payload(status="cancelled")
        clean_response = service.update(data["id"], clean_payload)
        assert clean_response.status_code == StatusCodes.OK

        factory.cleanup(listener_id)



    @allure.story("Create subscription with empty body")
    def test_create_subs_missing_fields(self, listener_service, subscription_service):
        """POST /subscriptions - with empty body should return 400.
        with message indicating which fields are missing.
        """
        service = subscription_service

        response = service.create({})

        self.using(response).assert_status_code_is(StatusCodes.BAD_REQUEST)
        self.using(response).assert_response_has_key("message")


    @allure.story("Create subscription with wrong typo fields")
    def test_create_subs_wrong_typo(self, listener_service, subscription_service):
        """POST /subscriptions - with wrong typo in 'plan' field.
        Should return 400 and message.
        """
        #create listener via Factory
        factory = ListenerFactory(listener_service)
        listener = factory.create()
        listener_id = listener["id"]

        service = subscription_service
        payload = subscription_create_payload(listener_id=listener_id, plan=True)
        response = service.create(payload)
        data = response.json()
        logger.info("DATA: %s ", data)

        self.using(response).assert_status_code_is(StatusCodes.BAD_REQUEST)
        self.using(response).assert_response_has_key("message")

        #CLEANUP
        factory.cleanup(listener_id)


    @allure.story("Create duplicated subscription for same listener")
    def test_create_duplicated_subs(self, listener_service, subscription_service):
        """POST /subscriptions - duplicated subscriptions should return 409 with message.
        """
        #create listener via Factory
        factory = ListenerFactory(listener_service)
        listener = factory.create()
        listener_id = listener["id"]

        #create first subscription
        service = subscription_service
        payload_1 = subscription_create_payload(listener_id=listener_id)

        response_1 = service.create(payload_1)
        data_1 = response_1.json()

        #create second subscription
        payload_2 = subscription_create_payload(listener_id=listener_id)

        response_2 = service.create(payload_2)

        self.using(response_2).assert_status_code_is(StatusCodes.CONFLICT)
        self.using(response_2).assert_response_has_key("message")

        #CLEANUP
        clean_payload = subscription_update_payload(status="cancelled")
        clean_response = service.update(data_1["id"], clean_payload)
        assert clean_response.status_code == StatusCodes.OK

        factory.cleanup(listener_id)

    @pytest.mark.subscription
    @allure.story("Create subscription for nonexistent listener")
    def test_create_nonexistent_listener(self, subscription_service):
        """POST /subscriptions - for nonexistent listener should return 404.
        and message.
        """

        #create subscription
        service = subscription_service
        payload = subscription_create_payload(listener_id=999999)

        response = service.create(payload)
        data = response.json()

        self.using(response).assert_status_code_is(StatusCodes.NOT_FOUND)
        self.using(response).assert_response_has_key("message")


@pytest.mark.subscription
@allure.feature("Subscriptions")
class TestSubscriptionRetrieval(BaseAssertions):
    """GET /subscriptions - GET /subscriptions?listener_id=
    - GET /subscriptions?status= - GET /subscriptions/<id>"""


    @allure.story("Get list subscriptions")
    def test_get_list_subs(self, subscription_service):
        """GET /subscriptions should return 200 with a list of subscriptions."""

        response = subscription_service.list()
        data = response.json()
        logger.info("DATA: %s", data)

        self.using(response).assert_status_code_is(StatusCodes.OK)
        self.using(response).assert_schema(SUBSCRIPTION_LIST_SCHEMA)


    @allure.story("Get list subscriptions filtered by listener_id")
    def test_get_list_subs_filtered_listener_id(self, listener_service, subscription_service):
        """GET /subscriptions - filtered by listener_id return 200 with a subscriptions
        matching with listener_id.
        """
        #create listener via Factory
        factory = ListenerFactory(listener_service)
        listener = factory.create()
        listener_id = listener["id"]

        #create subscription
        service = subscription_service
        payload = subscription_create_payload(listener_id=listener_id)
        response = service.create(payload)
        data = response.json()

        #get subscription filtered by listener_id
        get_response = service.list(listener_id=listener_id)
        get_data = get_response.json()

        self.using(get_response).assert_status_code_is(StatusCodes.OK)
        assert  all(subscription["listener_id"] == listener_id for subscription in get_data)

        #CLEANUP
        clean_payload = subscription_update_payload(status="cancelled")
        clean_response = service.update(data["id"], clean_payload)
        assert clean_response.status_code == StatusCodes.OK

        factory.cleanup(listener_id)


    @allure.story("Get list subscriptions filtered by status")
    def test_get_list_subs_filtered_status(self, listener_service, subscription_service):
        """GET /subscriptions - filtered by 'status' return 200 with a subscriptions
        matching with 'status'.
        """
        #create listener via Factory
        factory = ListenerFactory(listener_service)
        listener = factory.create()
        listener_id = listener["id"]

        #create subscription
        service = subscription_service
        payload = subscription_create_payload(listener_id=listener_id)
        response = service.create(payload)
        data = response.json()

        #update subscription status
        update_payload = subscription_update_payload(status="cancelled")
        update_response = service.update(data["id"], update_payload)
        self.using(update_response).assert_status_code_is(StatusCodes.OK)

        #get subscription filtered by listener_id
        get_response = service.list(status="cancelled")
        get_data = get_response.json()

        self.using(get_response).assert_status_code_is(StatusCodes.OK)
        assert  all(subscription["status"] == "cancelled" for subscription in get_data)

        #CLEANUP

        factory.cleanup(listener_id)


    @allure.story("Get subscription by id")
    def test_get_by_id(self, listener_service, subscription_service):
        """GET /subscriptions/<id> - should return 200 and subscription matching
        with id.
        """
        #create listener via Factory
        factory = ListenerFactory(listener_service)
        listener = factory.create()
        listener_id = listener["id"]

        #create subscription
        service = subscription_service
        payload = subscription_create_payload(listener_id=listener_id)
        response = subscription_service.create(payload)
        data = response.json()

        #get subscription by id
        get_response = service.get_by_id(data["id"])

        self.using(get_response).assert_status_code_is(StatusCodes.OK)
        self.using(get_response).assert_response_has_key_value("id", data["id"])
        self.using(get_response).assert_schema(SUBSCRIPTION_RESPONSE_SCHEMA)

        #CLEANUP
        clean_payload = subscription_update_payload(status="cancelled")
        clean_response = service.update(data["id"], clean_payload)
        assert clean_response.status_code == StatusCodes.OK

        factory.cleanup(listener_id)


    @allure.story("Get nonexistent subscription")
    def test_get_non_existent_subs(self, subscription_service):
        """GET /subscriptions/999999 - should return 404 and message."""

        response = subscription_service.get_by_id(999999)

        self.using(response).assert_status_code_is(StatusCodes.NOT_FOUND)
        self.using(response).assert_response_has_key("message")


@pytest.mark.subscription
@allure.feature("Subscriptions")
class TestSubscriptionsStatusMachine(BaseAssertions):
    """Test for PUT /subscriptions/<id>."""

    @pytest.mark.parametrize("new_status", ["cancelled", "paused"])
    @allure.story("Update subscription status start in active.")
    def test_update_status_start_in_active(self, listener_service, subscription_service, new_status):
        """PUT /subscriptions/<id> - should update the proved fields and return 200.
        Only the specified fields change; others remain untouched.

        status machine:
        active -> cancelled/paused
        paused -> active/cancelled
        cancelled/expired = TERMINAL
        """
        #create listener via Factory
        factory = ListenerFactory(listener_service)
        listener = factory.create()
        listener_id = listener["id"]

        #create subscription
        service = subscription_service
        payload = subscription_create_payload(listener_id=listener_id)

        response = service.create(payload)
        data = response.json()

        #update status
        update_payload = subscription_update_payload(status=new_status)
        update_response = service.update(data["id"], update_payload)
        update_data = update_response.json()

        self.using(update_response).assert_status_code_is(StatusCodes.OK)
        self.using(update_response).assert_response_has_key_value("status", new_status)
        if update_data["status"] == "paused":
            assert update_data["paused_at"] is not None
        if update_data["status"] == "cancelled":
            assert update_data["cancelled_at"] is not None

        #CLEANUP
        if update_data["status"] == "paused":
            payload = subscription_update_payload(status="cancelled")
            response = service.update(update_data["id"], payload)
            assert response.status_code == StatusCodes.OK

        factory.cleanup(listener_id)


    @pytest.mark.parametrize("new_status", ["cancelled", "active"])
    @allure.story("Update subscription status start in paused.")
    def test_update_status_start_in_paused(self, listener_service, subscription_service, new_status):
        """PUT /subscriptions/<id> - should update the proved fields and return 200.
        Only the specified fields change; others remain untouched.

        status machine:
        active -> cancelled/paused
        paused -> active/cancelled
        cancelled/expired = TERMINAL
        """
        #create listener via Factory
        factory = ListenerFactory(listener_service)
        listener = factory.create()
        listener_id = listener["id"]

        #create subscription
        service = subscription_service
        payload = subscription_create_payload(listener_id=listener_id)

        response = service.create(payload)
        data = response.json()

        #update status active -> paused
        update_payload = subscription_update_payload(status="paused")
        update_response = service.update(data["id"], update_payload)

        #update status machine
        status_payload = subscription_update_payload(status=new_status)
        status_response = service.update(data["id"],status_payload)
        status_data = status_response.json()

        self.using(status_response).assert_status_code_is(StatusCodes.OK)
        self.using(status_response).assert_response_has_key_value("status", new_status)
        if status_data["status"] == "active":
            assert status_data["paused_at"] is None
        if status_data["status"] == "cancelled":
            assert status_data["cancelled_at"] is not None

        #CLEANUP
        if status_data["status"] == "active":
            payload = subscription_update_payload(status="cancelled")
            response = service.update(status_data["id"], payload)
            assert response.status_code == StatusCodes.OK

        factory.cleanup(listener_id)


    @pytest.mark.parametrize("new_status", ["active", "paused"])
    @allure.story("Update subscription status start in cancelled.")
    def test_update_status_start_in_cancelled(self, listener_service, subscription_service, new_status):
        """PUT /subscriptions/<id> - should return 400, and message.

        status machine:
        active -> cancelled/paused
        paused -> active/cancelled
        cancelled/expired = TERMINAL
        """
        #create listener via Factory
        factory = ListenerFactory(listener_service)
        listener = factory.create()
        listener_id = listener["id"]

        #create subscription
        service = subscription_service
        payload = subscription_create_payload(listener_id=listener_id)

        response = service.create(payload)
        data = response.json()

        #update status active -> paused
        update_payload = subscription_update_payload(status="cancelled")
        update_response = service.update(data["id"], update_payload)

        #update status machine
        status_payload = subscription_update_payload(status=new_status)
        status_response = service.update(data["id"],status_payload)

        self.using(status_response).assert_status_code_is(StatusCodes.BAD_REQUEST)
        self.using(status_response).assert_response_has_key("message")

        #CLEANUP

        factory.cleanup(listener_id)

@pytest.mark.subscription
@allure.feature("Subscriptions")
class TestUpdateSubscriptions(BaseAssertions):
    """PUT /subscriptions/<id>."""

    @allure.story("Update plan to basic.")
    def test_update_plan_to_basic(self, listener_service, subscription_service):
        """PUT /subscriptions/<id> - update plan form 'free' to 'basic', should return 200.
        expires_at must change 30 days.
        """
        #create listener via Factory
        factory = ListenerFactory(listener_service)
        listener = factory.create()
        listener_id = listener["id"]

        #create subscription
        service = subscription_service
        payload = subscription_create_payload(listener_id=listener_id)

        response = service.create(payload)
        data = response.json()

        #update plan free -> basic
        update_payload = subscription_update_payload(plan="basic")
        update_response = service.update(data["id"], update_payload)
        update_data = update_response.json()

        time_update_plan = datetime.fromisoformat(
            update_data["updated_at"].replace("Z", "+00:00")
        )
        time_expire_plan = datetime.fromisoformat(
            update_data["expires_at"].replace("Z", "+00:00")
        )

        self.using(update_response).assert_status_code_is(StatusCodes.OK)
        assert  time_expire_plan == time_update_plan + timedelta(days=30)

        #CLEANUP
        clean_payload = subscription_update_payload(status="cancelled")
        clean_response = service.update(data["id"], clean_payload)
        assert clean_response.status_code == StatusCodes.OK

        factory.cleanup(listener_id)


    @allure.story("Update plan to premium.")
    def test_update_plan_to_premium(self, listener_service, subscription_service):
        """PUT /subscriptions/<id> - update plan form 'free' to 'premium', should return 200.
        expires_at must change 365 days.
        """
        #create listener via Factory
        factory = ListenerFactory(listener_service)
        listener = factory.create()
        listener_id = listener["id"]

        #create subscription
        service = subscription_service
        payload = subscription_create_payload(listener_id=listener_id)

        response = service.create(payload)
        data = response.json()

        #update plan free -> premium
        update_payload = subscription_update_payload(plan="premium")
        update_response = service.update(data["id"], update_payload)
        update_data = update_response.json()

        time_update_plan = datetime.fromisoformat(
            update_data["updated_at"].replace("Z", "+00:00")
        )
        time_expire_plan = datetime.fromisoformat(
            update_data["expires_at"].replace("Z", "+00:00")
        )

        self.using(update_response).assert_status_code_is(StatusCodes.OK)
        assert  time_expire_plan == time_update_plan + timedelta(days=365)

        #CLEANUP
        clean_payload = subscription_update_payload(status="cancelled")
        clean_response = service.update(data["id"], clean_payload)
        assert clean_response.status_code == StatusCodes.OK

        factory.cleanup(listener_id)


    @allure.story("Update plan to subscription paused.")
    def test_update_plan_to_subs_paused(self, listener_service, subscription_service):
        """PUT /subscriptions/<id> - update plan to subscription with status 'paused'
        should return 400 and message.
        """
        #create listener via Factory
        factory = ListenerFactory(listener_service)
        listener = factory.create()
        listener_id = listener["id"]

        #create subscription
        service = subscription_service
        payload = subscription_create_payload(listener_id=listener_id)

        response = service.create(payload); data = response.json()

        #update status active -> paused
        update_status_payload = subscription_update_payload(status="paused")
        update_status_response = service.update(data["id"], update_status_payload)

        #update plan free -> premium
        update_plan_payload = subscription_update_payload(plan="premium")
        update_plan_response = service.update(data["id"], update_plan_payload)

        self.using(update_plan_response).assert_status_code_is(StatusCodes.BAD_REQUEST)
        self.using(update_plan_response).assert_response_has_key("message")

        #CLEANUP
        clean_payload = subscription_update_payload(status="cancelled")
        clean_response = service.update(data["id"], clean_payload)
        assert clean_response.status_code == StatusCodes.OK

        factory.cleanup(listener_id)





