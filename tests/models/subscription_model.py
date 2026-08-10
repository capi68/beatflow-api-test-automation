"""Subscription domain model."""

from tests.base.base_model import BaseModel

class Subscription(BaseModel):
    """Represents a subscription Entity."""

    def __init__(
            self,
            listener_id: int | None = None,
            plan: str = "free",
    ):
        super().__init__()
        self.listener_id = listener_id
        self.plan = plan