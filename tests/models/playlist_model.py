"""Playlist domain model."""

from tests.base.base_model import BaseModel

class Playlist(BaseModel):
    """Represents a playlist Entity."""

    def __init__(
            self,
            listener_id: int | None = None,
            name: str = "Hip Hop 00",
            description: str = "Best Hip Hop songs of 00",
            is_public: bool = False,
            track_count: int = 0,
    ):
        super().__init__()
        self.listener_id = listener_id
        self.name = name
        self.description = description
        self.is_public = is_public
        self.track_count = track_count