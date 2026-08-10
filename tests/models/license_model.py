"""License domain model."""

from tests.base.base_model import BaseModel

class License(BaseModel):
    """Represents a license entity."""

    def __init__(
            self,
            track_id: int | None = None,
            licensee_name: str = "Universal Music Publishing Group",
            licensee_email: str | None = None,
            license_type: str = "sync",
            status: str = "requested",
            fee: float = 500.00,
            territory: str = "worldwide",
            starts_at: str = "2026-07-31",
            expires_at: str = "2026-08-31",
    ):
        super().__init__()
        self.track_id = track_id
        self.licensee_name = licensee_name
        self.licensee_email = licensee_email
        self.licensee_type = license_type
        self.status = status
        self.fee = fee
        self.territory = territory
        self.starts_at = starts_at
        self.expires_at = expires_at