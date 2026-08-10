"""Royalty domain model."""

from tests.base.base_model import BaseModel

class Royalty(BaseModel):
    """Represents a royalty entity belonging to a royalty."""

    def __init__(
            self,
            artist_id: int | None = None,
            track_id: int | None = None,
            stream_count: int = 1500,
            amount: float = 4.5,
            period_start: str = "2026-01-01",
            period_end: str = "2026-01-31",
    ):
        super().__init__()
        self.artist_id = artist_id
        self.track_id = track_id
        self.stream_count = stream_count
        self.amount = amount
        self.period_start = period_start
        self.period_end = period_end