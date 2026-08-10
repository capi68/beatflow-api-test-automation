"""Payload builder for Stream API requests."""

from tests.models.streams_model import Stream

def create_stream_payload(stream: Stream = None, listener_id: int = None, track_id: int = None, **overrides) -> dict:
    """Build a valid payload for POST /streams."""

    if stream is None:
        stream = Stream()

    payload = {
        "listener_id": listener_id or stream.listener_id,
        "track_id": track_id or stream.track_id,
        "duration_seconds": stream.duration_seconds,
    }
    payload.update(overrides)

    return  payload

