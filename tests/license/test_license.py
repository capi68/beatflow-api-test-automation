"""Tests for API license."""

import allure
import pytest

from tests.base.base_assertions import BaseAssertions
from tests.models.license_model import License
from tests.payloads.license_payloads import license_create_payload, license_update_payload
from tests.schemas.license_schemas import LICENSE_RESPONSE_SCHEMA, LICENSE_LIST_SCHEMA
from tests.factories.track_factory import TrackFactory
from tests.factories.license_factory import LicenseFactory
from tests.utils.constants import StatusCodes
from tests.utils.logger import get_logger

logger = get_logger(__name__)

@pytest.mark.license
@allure.feature("Licenses")
class TestLicenseCreate(BaseAssertions):
    """POST /licenses - license registration.
    Validates that the license creation endpoint correctly handles
    valid input, missing fields valid data, and duplicate emails."""


    @allure.story("Create license successfully")
    def test_create_license_success(self, license_service, artist_service, album_service, track_service):
        """POST /licenses - with valid data should return 201
        with a response matching the License response schema."""
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

        self.using(response).assert_status_code_is(StatusCodes.CREATED)
        self.using(response).assert_response_has_key("id")
        self.using(response).assert_schema(LICENSE_RESPONSE_SCHEMA)
        self.using(response).assert_response_has_key_value("licensee_email", payload["licensee_email"])
        self.using(response).assert_response_has_key_value("track_id", track_id)

        #CLEANUP
        service.update(data["id"], {"status": "revoked", "revocation_reason": "revocation reason"})
        factory.cleanup(track_id)
        factory.cleanup_all(track["album_id"],track["artist_id"])


    @allure.story("Create license with missing required fields")
    def test_create_license_missing_fields(self, license_service, artist_service, album_service, track_service):
        """POST /licenses - with empty body should return 400 with message."""

        response = license_service.create({})

        self.using(response).assert_status_code_is(StatusCodes.BAD_REQUEST)
        self.using(response).assert_response_has_key("message")


    @allure.story("Create license with invalid email")
    def test_create_license_invalid_email(self, license_service, artist_service, album_service, track_service):
        """POST /licenses - with invalid email should return 400 and message."""
        #create track via Factory
        factory = TrackFactory(artist_service, album_service, track_service)
        track = factory.create()
        track_id = track["id"]

        #create license
        service = license_service
        license = License(track_id=track_id)
        payload = license_create_payload(license, licensee_email="is_not_email")
        response = service.create(payload)
        data = response.json()

        self.using(response).assert_status_code_is(StatusCodes.BAD_REQUEST)
        self.using(response).assert_response_has_key("message")

        #CLEANUP
        factory.cleanup(track_id)
        factory.cleanup_all(track["album_id"],track["artist_id"])


    @allure.story("Create license empty required fields")
    @pytest.mark.parametrize("field", ["track_id","licensee_name","licensee_email","license_type","fee"])
    def test_create_license_empty_required_fields(self, license_service, artist_service, album_service, track_service, field):
        """POST /licenses - with empty required fields should return 400 and message"""
        #create track via Factory
        factory = TrackFactory(artist_service, album_service, track_service)
        track = factory.create()
        track_id = track["id"]

        #create license
        service = license_service
        license = License(track_id=track_id)
        payload = license_create_payload(license)
        payload[field] = ""
        response = service.create(payload)
        data = response.json()

        self.using(response).assert_status_code_is(StatusCodes.BAD_REQUEST)
        self.using(response).assert_response_has_key("message")

        #CLEANUP
        factory.cleanup(track_id)
        factory.cleanup_all(track["album_id"],track["artist_id"])


    @allure.story("Create license nonexistent track_id")
    def test_create_license_nonexistent_track_id(self, license_service, artist_service, album_service, track_service):
        """POST /licenses - with nonexistent track_id should return 404 and message"""

        service = license_service
        license = License(track_id=999999)
        payload = license_create_payload(license)
        response = service.create(payload)

        self.using(response).assert_status_code_is(StatusCodes.NOT_FOUND)
        self.using(response).assert_response_has_key("message")


    @allure.story("Create license for unavailable track")
    def test_create_license_for_unavailable_track(self, license_service, artist_service, album_service, track_service):
        """POST /licenses - for unavailable track should return 400 and message"""
        #create track via Factory
        factory = TrackFactory(artist_service, album_service, track_service)
        track = factory.create()
        track_id = track["id"]
        track_service.update(track_id, {"is_available": False})

        #create license
        service = license_service
        license = License(track_id=track_id)
        payload = license_create_payload(license)
        response = service.create(payload)

        self.using(response).assert_status_code_is(StatusCodes.BAD_REQUEST)
        self.using(response).assert_response_has_key("message")

        #CLEANUP
        factory.cleanup(track_id)
        factory.cleanup_all(track["album_id"],track["artist_id"])


    @allure.story("Create license with valid and invalid license types")
    @pytest.mark.parametrize("value", ["sync", "mechanical", "performance", "master", "distribution"])
    def test_create_license_type_validation(self, license_service, artist_service, album_service, track_service, value):
        """POST /licenses - with valid and invalid license types should return 201 if is valid
        and 400 if is invalid and message"""
        #create track via Factory
        factory = TrackFactory(artist_service, album_service, track_service)
        track = factory.create()
        track_id = track["id"]

        #create license
        service = license_service
        license = License(track_id=track_id)
        payload = license_create_payload(license)
        payload["license_type"] = value
        response = service.create(payload)
        data = response.json()

        if payload["license_type"] == "distribution":
            self.using(response).assert_status_code_is(StatusCodes.BAD_REQUEST)
            self.using(response).assert_response_has_key("message")

        if payload["license_type"] != "distribution":
            self.using(response).assert_status_code_is(StatusCodes.CREATED)
            self.using(response).assert_response_has_key_value("license_type", value)
            service.update(data["id"], {"status": "revoked", "revocation_reason": "revocation reason"})

        #CLEANUP
        factory.cleanup(track_id)
        factory.cleanup_all(track["album_id"],track["artist_id"])


    @allure.story("Create license fee boundary values")
    @pytest.mark.parametrize("value", [99, 1000001])
    def test_create_license_fee_boundary_values(self, license_service, artist_service, album_service, track_service, value):
        """POST /licenses - with fee boundary values should return 400 and message"""
        #create track via Factory
        factory = TrackFactory(artist_service, album_service, track_service)
        track = factory.create()
        track_id = track["id"]

        #create license
        service = license_service
        license = License(track_id=track_id)
        payload = license_create_payload(license, fee=value)
        response = service.create(payload)

        self.using(response).assert_status_code_is(StatusCodes.BAD_REQUEST)
        self.using(response).assert_response_has_key("message")

        #CLEANUP
        factory.cleanup(track_id)
        factory.cleanup_all(track["album_id"],track["artist_id"])


    @allure.story("Create license with exceed maxLength 'territory' field")
    def test_create_license_exceed_max_length_territory(self, license_service, artist_service, album_service, track_service):
        """POST /licenses - with exceed maxLength 'territory' field should return 400 and message"""
        #create track via Factory
        factory = TrackFactory(artist_service, album_service, track_service)
        track = factory.create()
        track_id = track["id"]

        #create license
        service = license_service
        license = License(track_id=track_id)
        payload = license_create_payload(license, territory="a" * 101)
        response = service.create(payload)

        self.using(response).assert_status_code_is(StatusCodes.BAD_REQUEST)
        self.using(response).assert_response_has_key("message")

        #CLEANUP
        factory.cleanup(track_id)
        factory.cleanup_all(track["album_id"],track["artist_id"])



    @allure.story("Create license with starts_at with invalid format")
    def test_create_license_starts_at_invalid_format(self, license_service, artist_service, album_service, track_service):
        """POST /licenses - with starts_at with invalid format should return 400 and message"""
        #create track via Factory
        factory = TrackFactory(artist_service, album_service, track_service)
        track = factory.create()
        track_id = track["id"]

        #create license
        service = license_service
        license = License(track_id=track_id)
        payload = license_create_payload(license, starts_at="15-01-2026")
        response = service.create(payload)

        self.using(response).assert_status_code_is(StatusCodes.BAD_REQUEST)
        self.using(response).assert_response_has_key("message")

        #CLEANUP
        factory.cleanup(track_id)
        factory.cleanup_all(track["album_id"],track["artist_id"])


    @allure.story("Create license with expires_at before starts_at")
    def test_create_license_expires_at_before_starts_at(self, license_service, artist_service, album_service, track_service):
        """POST /licenses - with expires_at before starts_at should return 400 and message"""
        #create track via Factory
        factory = TrackFactory(artist_service, album_service, track_service)
        track = factory.create()
        track_id = track["id"]

        #create license
        service = license_service
        license = License(track_id=track_id)
        payload = license_create_payload(license, starts_at="2026-01-15", expires_at="2025-01-15")
        response = service.create(payload)

        self.using(response).assert_status_code_is(StatusCodes.BAD_REQUEST)
        self.using(response).assert_response_has_key("message")

        #CLEANUP
        factory.cleanup(track_id)
        factory.cleanup_all(track["album_id"],track["artist_id"])


    @allure.story("Create two licenses type for same track")
    def test_create_two_license_type_for_same_track(self, license_service, artist_service, album_service, track_service):
        """POST /licenses - with two licenses type for same track should return 409 and message"""
        #create track via Factory
        factory = TrackFactory(artist_service, album_service, track_service)
        track = factory.create()
        track_id = track["id"]

        service = license_service
        license = License(track_id=track_id)

        #create license 1
        payload = license_create_payload(license)
        response = service.create(payload)
        data = response.json()

        #create license 2
        payload_2 = license_create_payload(license)
        response_2 = service.create(payload)

        self.using(response_2).assert_status_code_is(StatusCodes.CONFLICT)
        self.using(response_2).assert_response_has_key("message")

        #CLEANUP
        service.update(data["id"], {"status": "revoked", "revocation_reason": "revocation reason"})
        factory.cleanup(track_id)
        factory.cleanup_all(track["album_id"],track["artist_id"])


@pytest.mark.license
@allure.feature("Licenses")
class TestLicenseRetrieval(BaseAssertions):
    """Test for GET /licenses - GET /licenses/<id>"""

    @allure.story("Get list of licenses")
    def test_licenses_list(self, license_service):
        """GET /licenses - should return 200 and a list of licenses."""

        response = license_service.list()

        self.using(response).assert_status_code_is(StatusCodes.OK)
        self.using(response).assert_schema(LICENSE_LIST_SCHEMA)


    @allure.story("Get list of licenses filtered by track_id")
    def test_license_list_by_track_id(self, license_service, artist_service, album_service, track_service):
        """GET /licenses?track_id= - should return 200 and a list of licenses filtered by track_id."""
        #create licens via factory
        factory = LicenseFactory(license_service, artist_service, album_service, track_service)
        license = factory.create()
        license_id = license["id"]

        #get license by track_id
        get_response = license_service.list(license["track_id"])
        get_data = get_response.json()

        self.using(get_response).assert_status_code_is(StatusCodes.OK)
        self.using(get_response).assert_schema(LICENSE_LIST_SCHEMA)
        assert all(licenses["track_id"] == license["track_id"] for licenses in get_data)

        #CLEANUP
        factory.clean_up(license_id)
        factory.cleanup_all(license["track_id"], license["album_id"], license["artist_id"])



    @allure.story("Get list of licenses filtered by status")
    def test_license_list_by_status(self, license_service, artist_service, album_service, track_service):
        """GET /licenses?status= - should return 200 and a list of licenses filtered by status."""
        #create licens via factory
        factory = LicenseFactory(license_service, artist_service, album_service, track_service)
        license = factory.create()
        license_id = license["id"]
        license_service.update(license_id, {"status": "approved"})

        #get license by track_id
        get_response = license_service.list(status="approved")
        get_data = get_response.json()

        self.using(get_response).assert_status_code_is(StatusCodes.OK)
        self.using(get_response).assert_schema(LICENSE_LIST_SCHEMA)
        assert all(licenses["status"] == "approved" for licenses in get_data)

        #CLEANUP
        factory.clean_up(license_id)
        factory.cleanup_all(license["track_id"], license["album_id"], license["artist_id"])


    @allure.story("Get list of licenses filtered by license_type")
    def test_license_list_by_license_type(self, license_service, artist_service, album_service, track_service):
        """GET /licenses?status= - should return 200 and a list of licenses filtered by license_type."""
        #create licens via factory
        factory = LicenseFactory(license_service, artist_service, album_service, track_service)
        license = factory.create(license_type="performance")
        license_id = license["id"]

        #get license by track_id
        get_response = license_service.list(license_type="performance")
        get_data = get_response.json()

        self.using(get_response).assert_status_code_is(StatusCodes.OK)
        self.using(get_response).assert_schema(LICENSE_LIST_SCHEMA)
        assert all(licenses["license_type"] == "performance" for licenses in get_data)

        #CLEANUP
        factory.clean_up(license_id)
        factory.cleanup_all(license["track_id"], license["album_id"], license["artist_id"])


    @allure.story("Get license by id")
    def test_license_by_id(self, license_service, artist_service, album_service, track_service):
        """GET /licenses/<id> - should return 200 and a license by id."""
        #create licens via factory
        factory = LicenseFactory(license_service, artist_service, album_service, track_service)
        license = factory.create()
        license_id = license["id"]

        #get license by track_id
        get_response = license_service.get_by_id(license_id)

        self.using(get_response).assert_status_code_is(StatusCodes.OK)
        self.using(get_response).assert_response_has_key_value("id", license_id)

        #CLEANUP
        factory.clean_up(license_id)
        factory.cleanup_all(license["track_id"], license["album_id"], license["artist_id"])


    @allure.story("Get nonexistent license.")
    def test_nonexistent_license(self, license_service, artist_service, album_service, track_service):
        """GET /licenses/999999 - should return 404 and message."""

        get_response = license_service.get_by_id(999999)

        self.using(get_response).assert_status_code_is(StatusCodes.NOT_FOUND)
        self.using(get_response).assert_response_has_key("message")


@pytest.mark.license
@allure.feature("Licenses")
class TestStatusMachine(BaseAssertions):
    """Test for status machine - PUT /licenses/<id>."""


    @allure.story("status machine starting in requested")
    @pytest.mark.parametrize("value", ["approved", "revoked"])
    def test_update_status_machine_starting_requested(self, license_service, artist_service, album_service, track_service, value):
        """only valid transition 'requested' > approved/revoked
        If status is 'approved' update approved_at."""
        #create licens via factory
        factory = LicenseFactory(license_service, artist_service, album_service, track_service)
        license = factory.create()
        license_id = license["id"]

        #update status
        update_payload = license_update_payload(status=value)
        if value == "revoked":
            update_payload["revocation_reason"] = "revocation reason"

        update_response = license_service.update(license_id, update_payload)
        update_data = update_response.json()

        self.using(update_response).assert_status_code_is(StatusCodes.OK)
        self.using(update_response).assert_response_has_key_value("id", license_id)
        if update_data["status"] == "approved":
            assert update_data["approved_at"] is not None

        #CLEANUP
        if update_data["status"] == "approved":
            factory.clean_up(license_id)
        factory.cleanup_all(license["track_id"], license["album_id"], license["artist_id"])


    @allure.story("invalid update status machine starting in requested")
    @pytest.mark.parametrize("value", ["active", "expired"])
    def test_invalid_update_status_machine_starting_requested(self, license_service, artist_service, album_service, track_service, value):
        """only valid transition 'requested' > approved/revoked"""
        #create licens via factory
        factory = LicenseFactory(license_service, artist_service, album_service, track_service)
        license = factory.create()
        license_id = license["id"]

        #update status
        update_payload = license_update_payload(status=value)
        update_response = license_service.update(license_id, update_payload)

        self.using(update_response).assert_status_code_is(StatusCodes.BAD_REQUEST)
        self.using(update_response).assert_response_has_key("message")

        #CLEANUP
        factory.clean_up(license_id)
        factory.cleanup_all(license["track_id"], license["album_id"], license["artist_id"])


    @allure.story("status machine starting in approved")
    @pytest.mark.parametrize("value", ["active", "revoked"])
    def test_update_status_machine_starting_approved(self, license_service, artist_service, album_service, track_service, value):
        """only valid transition 'approved' > active/revoked
        if status is 'active' update starts_at"""
        #create licens via factory
        factory = LicenseFactory(license_service, artist_service, album_service, track_service)
        license = factory.create()
        license_id = license["id"]
        license_service.update(license_id, {"status": "approved"})

        #update status
        update_payload = license_update_payload(status=value)
        if value == "revoked":
            update_payload["revocation_reason"] = "revocation reason"

        update_response = license_service.update(license_id, update_payload)
        update_data = update_response.json()

        self.using(update_response).assert_status_code_is(StatusCodes.OK)
        self.using(update_response).assert_response_has_key_value("id", license_id)
        if update_data["status"] == "active":
            assert update_data["starts_at"] is not None


        #CLEANUP
        if update_data["status"] == "active":
            factory.clean_up(license_id)
        factory.cleanup_all(license["track_id"], license["album_id"], license["artist_id"])


    @allure.story("invalid update status machine starting in approved")
    @pytest.mark.parametrize("value", ["requested", "expired"])
    def test_invalid_update_status_machine_starting_approved(self, license_service, artist_service, album_service, track_service, value):
        """only valid transition 'approved' > requested/expired"""
        #create licens via factory
        factory = LicenseFactory(license_service, artist_service, album_service, track_service)
        license = factory.create()
        license_id = license["id"]
        license_service.update(license_id, {"status": "approved"})

        #update status
        update_payload = license_update_payload(status=value)
        update_response = license_service.update(license_id, update_payload)

        self.using(update_response).assert_status_code_is(StatusCodes.BAD_REQUEST)
        self.using(update_response).assert_response_has_key("message")

        #CLEANUP
        factory.clean_up(license_id)
        factory.cleanup_all(license["track_id"], license["album_id"], license["artist_id"])


    @allure.story("status machine starting in active")
    @pytest.mark.parametrize("value", ["expired", "revoked"])
    def test_update_status_machine_starting_active(self, license_service, artist_service, album_service, track_service, value):
        """only valid transition 'active' > expired/revoked"""
        #create licens via factory
        factory = LicenseFactory(license_service, artist_service, album_service, track_service)
        license = factory.create()
        license_id = license["id"]
        license_service.update(license_id, {"status": "approved"})
        license_service.update(license_id, {"status": "active"})

        #update status
        update_payload = license_update_payload(status=value)
        if value == "revoked":
            update_payload["revocation_reason"] = "revocation reason"

        update_response = license_service.update(license_id, update_payload)
        update_data = update_response.json()

        self.using(update_response).assert_status_code_is(StatusCodes.OK)
        self.using(update_response).assert_response_has_key_value("id", license_id)

        #CLEANUP
        factory.clean_up(license_id)
        factory.cleanup_all(license["track_id"], license["album_id"], license["artist_id"])


    @allure.story("invalid update status machine starting in active")
    @pytest.mark.parametrize("value", ["requested", "approved"])
    def test_invalid_update_status_machine_starting_active(self, license_service, artist_service, album_service, track_service, value):
        """only valid transition 'active' > requested/approved"""
        #create licens via factory
        factory = LicenseFactory(license_service, artist_service, album_service, track_service)
        license = factory.create()
        license_id = license["id"]
        license_service.update(license_id, {"status": "approved"})
        license_service.update(license_id, {"status": "active"})

        #update status
        update_payload = license_update_payload(status=value)
        update_response = license_service.update(license_id, update_payload)

        self.using(update_response).assert_status_code_is(StatusCodes.BAD_REQUEST)
        self.using(update_response).assert_response_has_key("message")

        #CLEANUP
        factory.clean_up(license_id)
        factory.cleanup_all(license["track_id"], license["album_id"], license["artist_id"])


@pytest.mark.license
@allure.feature("Licenses")
class TestSideEffects(BaseAssertions):
    """side effects with status revoked"""


    @allure.story("license status revoked update track is_available field to False")
    def test_revoked_status_becomes_track_unavailable(self, license_service, artist_service, album_service, track_service):
        """license status revoked update track is_available field to False"""
        #create licens via factory
        factory = LicenseFactory(license_service, artist_service, album_service, track_service)
        license = factory.create()
        license_id = license["id"]
        license_service.update(license_id, {"status": "revoked", "revocation_reason": "revocation reason"})

        #get track data
        get_response = track_service.get_by_id(license["track_id"])
        get_data = get_response.json()

        self.using(get_response).assert_response_has_key_value("is_available", False)

        #CLEANUP
        factory.cleanup_all(license["track_id"], license["album_id"], license["artist_id"])

