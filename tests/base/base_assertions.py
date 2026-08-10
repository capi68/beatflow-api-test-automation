"""Chainable assertion class for API response validation."""

from typing import Any
from jsonschema import validate
import requests

from tests.utils.logger import get_logger

logger = get_logger(__name__)

class BaseAssertions:
    """Provides chainable assertion methods for HTTP responses.

    Usage:
    self.using(response).assert_status_code_is(200).assert_response_has_key("id").
    """

    _value: Any = None

    def using(self, value: Any) -> "BaseAssertions":
        """Set the value to assert against."""
        self._value = value
        return self

    def assert_status_code_is(self, expected: int) -> "BaseAssertions":
        """Assert the HTTP response status code matches expected."""
        actual = self._value.status_code
        assert  actual == expected, f"Expected status {expected}, got {actual}. Body: {self._value.text[:300]}"
        logger.info("Status code is %s", actual)
        return self

    def assert_status_code_is_not(self, excluded: int) -> "BaseAssertions":
        """Assert the status code is NOT the excluded value."""
        actual = self._value.status_code
        assert actual != excluded, f"Expected status NOT to be {excluded}, but it is."
        logger.info("Status code %s is not %s", actual, excluded)
        return self

    def assert_response_has_key(self, key: str) -> "BaseAssertions":
        """Assert the JSON response contains the given key."""
        data = self._value.json()
        assert key in data, f"Key '{key}' not found in response: {list(data.keys())}"
        logger.info("Response has key '%s'", key)
        return self

    def assert_response_key_absent(self, key: str) -> "BaseAssertions":
        """Assert the JSON response does NOT contain the given key."""
        data = self._value.json()
        assert key not in data, f"Key '{key}' should be absent but exist in response."
        logger.info("Key is %s is absent", key)
        return self

    def assert_response_has_key_value(self, key: str, expected_value: Any) -> "BaseAssertions":
        """Assert a specific key has the expected vale."""
        data = self._value.json()
        actual = data.get(key)
        assert actual == expected_value, f"Key '{key}': expected '{expected_value}', got '{actual}'"
        logger.info("Key '%s' = '%s'", key, expected_value)
        return self

    def assert_schema(self, schema: dict) -> "BaseAssertions":
        """Validate the response JSON against a JSON schema."""
        validate(instance=self._value.json(), schema=schema)
        logger.info("Schema validation passed")
        return self

    def assert_response_is_list(self) -> "BaseAssertions":
        """Assert the response body is a JSON array."""
        data = self._value.json()
        assert isinstance(data, list), f"Expected list, got {type(data).__name__}"
        logger.info("Response is a list.")
        return self

    def assert_list_not_empty(self) -> "BaseAssertions":
        """Assert the JSON array is not empty."""

        data = self._value.json()
        assert len(data) > 0, f"Expected non-empty list"
        logger.info("List has %s items", len(data))
        return self

    def assert_message_contains(self, substring: str) -> "BaseAssertions":
        """Assert the 'message' field contains a substring."""
        data = self._value.json()
        message = data.get("message", "")
        assert substring.lower() in message.lower(), f"Message '{message}' does not contains '{substring}'"
        logger.info("Message contain '%s'", substring)
        return self


