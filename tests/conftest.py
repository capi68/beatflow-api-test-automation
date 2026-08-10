"""Root conftest - shared fixtures for the entire test suite.

Fixtures at two scopes:
- session: auth tokens, service instances shared across all tests
- functions: fresh data per individual test.
"""

import  pytest
from tests.config.settings import config
from tests.services.artist_service import ArtistService
from tests.services.album_service import AlbumService
from tests.services.license_service import LicenseService
from tests.services.listener_service import ListenerService
from tests.payloads.artist_payload import artist_login_payload
from tests.payloads.listener_payload import listener_login_payload
from tests.services.playlist_service import PlaylistService
from tests.services.playlist_track_service import PlaylistTrackService
from tests.services.royalty_service import RoyaltyService
from tests.services.subscriptions_service import SubscriptionService
from tests.services.stream_service import StreamService
from tests.services.track_service import TrackService
from tests.utils.logger import get_logger

logger = get_logger(__name__)

# ─────────────────────────────────────────────────────────────
#  SESSION SCOPE — Artist
# ─────────────────────────────────────────────────────────────

@pytest.fixture(scope="session")
def artist_auth_token():
    """Authenticate with admin artist credentials and return JWT token.

    This fixture runs once per session. All tests share this token.
    """
    service = ArtistService()
    payload = artist_login_payload(
        email=config.admin_artist_email,
        password=config.admin_artist_password,
    )
    response = service.login(payload)
    assert response.status_code == 200, f"Auth  failed: {response.text}"
    token = response.json()["token"]
    logger.info("Session auth token obtained (artist)")
    return token

@pytest.fixture(scope="session")
def artist_service(artist_auth_token):
    """Provide an authenticated ArtistService for the session."""
    return ArtistService(token=artist_auth_token)

@pytest.fixture(scope="session")
def album_service(artist_auth_token):
    """Provide an authenticated AlbumService for the session."""
    return AlbumService(artist_auth_token)

@pytest.fixture(scope="session")
def track_service(artist_auth_token):
    """Provide an authenticated TrackService for the session."""
    return TrackService(artist_auth_token)

@pytest.fixture(scope="session")
def royalty_service(artist_auth_token):
    """Provide an authenticated RoyaltyService for the session."""
    return RoyaltyService(artist_auth_token)

@pytest.fixture(scope="session")
def license_service(artist_auth_token):
    """Provide an authenticated LicenseService for the session."""
    return LicenseService(artist_auth_token)


# ─────────────────────────────────────────────────────────────
#  SESSION SCOPE — Listener
# ─────────────────────────────────────────────────────────────

@pytest.fixture(scope="session")
def listener_auth_token():
    """Authenticate with admin listener credentials and return JWT token.

    This fixture runs once per session. All tests share this token.
    """
    service = ListenerService()
    payload = listener_login_payload(
        email=config.admin_listener_email,
        password=config.admin_listener_password,
    )
    response = service.login(payload)
    assert response.status_code == 200, f"Auth  failed: {response.text}"
    token = response.json()["token"]
    logger.info("Session auth token obtained (listener)")
    return token

@pytest.fixture(scope="session")
def listener_service(listener_auth_token):
    """Provide an authenticated ArtistService for the session."""
    return ListenerService(token=listener_auth_token)

@pytest.fixture(scope="session")
def subscription_service(listener_auth_token):
    """Provide an authenticated SubscriptionService for the session."""
    return SubscriptionService(listener_auth_token)

@pytest.fixture(scope="session")
def playlist_service(listener_auth_token):
    """Provide an authenticated PlaylistService for the session."""
    return PlaylistService(listener_auth_token)

@pytest.fixture(scope="session")
def playlist_track_service(listener_auth_token):
    """Provide an authenticated PlaylistTrackService for the session."""
    return PlaylistTrackService(listener_auth_token)

@pytest.fixture(scope="session")
def stream_service(listener_auth_token):
    """Provide an authenticated StreamService for the session."""
    return StreamService(listener_auth_token)

