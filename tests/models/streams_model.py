"""Stream domain model."""

from tests.base.base_model import BaseModel

class Stream:
    """Represents stream entity."""

    def __init__(
            self,
            listener_id: int | None = None,
            track_id: int | None = None,
            duration_seconds: int = 180
    ):
        super().__init__()
        self.listener_id = listener_id
        self.track_id = track_id
        self.duration_seconds = duration_seconds