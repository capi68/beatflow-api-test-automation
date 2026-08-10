"""Payload builders from royalty API requests."""

from tests.models.royalty_model import Royalty

def create_royalty_payload(royalty: Royalty = None, artist_id: int = None, track_id: int = None, **overrides) -> dict:
    """Build a valid payload for POST /royalties."""

    if royalty is None:
        royalty = Royalty()

    payload = {
        "artist_id": artist_id or royalty.artist_id,
        "track_id": track_id or royalty.track_id,
        "stream_count": royalty.stream_count,
        "amount": royalty.amount,
        "period_start": royalty.period_start,
        "period_end": royalty.period_end
    }
    payload.update(overrides)
    return payload

def update_royalty_payload(**kwargs) -> dict:
    """Build a payload for PUT /royalties/<id> with only provide fields."""
    return {k: v for k, v in kwargs.items() if v is not None}