import math
from typing import Generic, List, TypeVar

from pydantic import BaseModel, computed_field

T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    """
    Generic pagination envelope returned by every list endpoint.

    Formula
    -------
    total        — COUNT(*) of all rows matching the applied filters
    pages        — ceil(total / limit)  → how many full pages exist
    has_next     — (offset + limit) < total  → is there a page after this one?
    has_previous — offset > 0               → is there a page before this one?

    Clients can use `has_next` / `has_previous` directly instead of
    re-fetching the backend just to discover whether more data exists.
    """

    items: List[T]
    total: int
    limit: int
    offset: int

    @computed_field  # type: ignore[misc]
    @property
    def pages(self) -> int:
        """Total number of pages for the current page size."""
        if self.limit <= 0:
            return 0
        return math.ceil(self.total / self.limit) if self.total > 0 else 1

    @computed_field  # type: ignore[misc]
    @property
    def has_next(self) -> bool:
        """True when a next page exists — client should not call backend to check."""
        return (self.offset + self.limit) < self.total

    @computed_field  # type: ignore[misc]
    @property
    def has_previous(self) -> bool:
        """True when a previous page exists."""
        return self.offset > 0