"""Listener domain model."""

from tests.base.base_model import BaseModel

class Listener(BaseModel):
    """Represents a listener Entity."""

    def __init__(
            self,
            username: str | None = None,
            email: str | None = None,
            password: str ="Listener123!",
            first_name: str ="Maria",
            last_name: str ="Santos",
            date_of_birth: str | None ="1992-08-17",
            country: str | None ="US"
    ):
        super().__init__()
        self.username = username
        self.email = email
        self.password = password
        self.first_name = first_name
        self.last_name = last_name
        self.date_of_birth = date_of_birth
        self.country = country