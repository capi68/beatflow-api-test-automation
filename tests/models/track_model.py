"""Track domain model."""

from tests.base.base_model import BaseModel
from tests.utils.constants import MusicGenres

class Track(BaseModel):
    """Represents a track entity belonging to an album."""

    def __init__(
            self,
            album_id: int | None = None,
            title: str = "Stan",
            duration_seconds: int = 404,
            track_number: int = 3,
            genre_id: int = MusicGenres.HIP_HOP,
            is_available: bool = True,
            is_explicit: bool = False,

    ):
        super().__init__()
        self.album_id =album_id
        self.title = title
        self.duration_seconds = duration_seconds
        self.track_number = track_number
        self.genre_id = genre_id
        self.is_available = is_available
        self.is_explicit = is_explicit