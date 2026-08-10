"""Album domain model."""

from typing import Optional
from tests.base.base_model import BaseModel
from tests.utils.constants import MusicGenres


class Album(BaseModel):
    """Represents an album entity belonging to an artist."""

    def __init__(
            self,
            artist_id: int | None = None,
            title: str = "Eminem Hits",
            description: Optional[str] = "All eminem hits in one album",
            release_year: Optional[int] = 2025,
            genre_id: int = MusicGenres.HIP_HOP,
            cover_url: Optional[str] = "https://example.com/covers/the-marshall-mathers-lp.jpg",
   ):
        super().__init__()
        self.artist_id = artist_id
        self.title = title
        self.description = description
        self.release_year = release_year
        self.genre_id = genre_id
        self.cover_url = cover_url