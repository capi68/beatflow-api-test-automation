"""Base model class for all domain objects."""

from typing import Optional, Any

class BaseModel:
    """Base class for domain models.

    Provides common interface for storing raw API response
    and managing entity state.
    """

    def __init__(self):
        self._raw_response: Optional[Any] = None
        self._id: Optional[int] = None

    @property
    def raw_response(self) -> Optional[Any]:
        return self._raw_response

    @raw_response.setter
    def raw_response(self, value:Any) -> None:
        self._raw_response = value

    @property
    def id(self) -> Optional[int]:
        return  self._id

    @id.setter
    def id(self, value: int) -> None:
        self._id = value
