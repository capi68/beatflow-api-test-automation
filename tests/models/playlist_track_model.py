"""Playlist Track domain model."""

from tests.base.base_model import BaseModel

class PlaylistTrack(BaseModel):
    """Represents a playlist Track Entity."""

    def __init__(
            self,
            playlist_id: int | None = None,
            track_id: int | None = None,
            position: int | None = None,
    ):
        super().__init__()
        self.playlist_id = playlist_id
        self.track_id = track_id
        self.position = position