"""Base service class providing HTTP plumbing for all service."""

from typing import Optional
import requests

from tests.config.settings import config
from tests.utils.logger import get_logger

logger = get_logger(__name__)

class BaseService:
    """Base HTTP service with authentication and request handling.

    All entity services inherit from this class to leverage
    common header management and request sending.
    """

    def __init__(self, token: Optional[str] = None):
        self._token = token
        self._base_url = config.base_url

    @property
    def token(self) -> Optional[str]:
        return  self._token

    @token.setter
    def token(self, value: str) -> None:
        self._token = value

    def _get_headers(self) -> dict:
        """Build headers with Content-Type and Authorization."""
        headers = {"Content-Type": "application/json", "Accept": "application/json"}
        if self._token:
            headers["Authorization"] = f"Bearer {self._token}"
        return headers

    def _get_url(self, endpoint: str) -> str:
        """Build full URL from base + endpoint."""
        return f"{self._base_url}{endpoint}"

    def _send_request(
            self,
            method: str,
            endpoint: str,
            data: Optional[dict] = None,
            params: Optional[dict] = None,
    ) -> requests.Response:
        """Send an HTTP request and log it."""
        url = self._get_url(endpoint)
        headers = self._get_headers()
        response = requests.request(
            method, url, headers=headers, json=data, params=params, timeout=(5, 10)
        )
        logger.info("Response: %s %s", response.status_code, response.text[:200])
        return response

    def get(self, endpoint: str, params: Optional[dict] = None) -> requests.Response:
        return  self._send_request("GET", endpoint, params=params)

    def post(self, endpoint: str, data: Optional[dict] = None) -> requests.Response:
        return self._send_request("POST", endpoint, data=data)

    def put(self, endpoint: str, data: Optional[dict] = None) -> requests.Response:
        return self._send_request("PUT", endpoint, data=data)

    def delete(self, endpoint: str) -> requests.Response:
        return self._send_request("DELETE", endpoint)