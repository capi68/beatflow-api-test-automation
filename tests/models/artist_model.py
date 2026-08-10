"""Artist domain model."""

from tests.base.base_model import BaseModel
from tests.utils.constants import MusicGenres

class Artist(BaseModel):
    """Represents an artist entity."""

    def __init__(
            self,
            stage_name: str = "eminem",
            first_name: str = "Marshall",
            last_name: str = "Mathers",
            email: str | None = None,
            password: str = "Artist123!",
            bio: str = (
                    "American rapper, songwriter, and record producer. "
                    "One of the best-selling artists of all time."
            ),
            genre_id: int = MusicGenres.HIP_HOP,
            country: str | None = "United States"
    ):
        super().__init__()
        self.stage_name = stage_name
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.password = password
        self.bio = bio
        self.genre_id = genre_id
        self.country = country
