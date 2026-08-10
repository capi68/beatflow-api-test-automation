"""Service layer for Streams API interactions."""

import  requests
from tests.base.base_service import BaseService
from tests.utils.endpoints import StreamsEndpoints

class StreamService(BaseService):
    """HTTP service for streams CRUD."""

    def list(self, listener_id: int = None, track_id: int = None) -> requests.Response:
        """GET /streams - list all streams of a track for one listener."""

        params = {}

        if listener_id is not None:
            params["listener_id"] = listener_id
        if track_id is not None:
            params["track_id"] = track_id
        return self.get(StreamsEndpoints.BASE, params=params)

    def create(self, payload: dict) -> requests.Response:
        """POST /streams - register a new stream."""
        return self.post(StreamsEndpoints.BASE, data=payload)

    def get_by_id(self, stream_id: int) -> requests.Response:
        """GET /streams/<id> - get stream by ID."""
        endpoint = StreamsEndpoints.DETAIL.format(stream_id=stream_id)
        return self.get(endpoint)