from typing import TypeVar

from fastapi import Query
from sqlmodel import Session
from sqlmodel.sql.expression import SelectOfScalar

from app.schemas.pagination import PaginatedResponse

T = TypeVar("T")


class PaginationParams:
    """
    Reusable FastAPI dependency for limit/offset pagination.
    Inject with: pagination: PaginationParams = Depends(PaginationParams)
    """

    def __init__(
        self,
        limit: int = Query(
            default=20, ge=1, le=100, description="Max records to return"
        ),
        offset: int = Query(default=0, ge=0, description="Number of records to skip"),
    ):
        self.limit = limit
        self.offset = offset


def paginate(
    db: Session,
    data_query: SelectOfScalar[T],
    count_query: SelectOfScalar[int],
    pagination: PaginationParams,
) -> PaginatedResponse[T]:
    """
    Executes both queries and returns a PaginatedResponse envelope.

    Parameters
    ----------
    db          : active database session
    data_query  : filtered SELECT query — without offset/limit applied
    count_query : filtered COUNT query  — same filters, no offset/limit
    pagination  : PaginationParams dependency injected by FastAPI
    """
    total: int = db.exec(count_query).one()
    items = list(db.exec(data_query.offset(pagination.offset).limit(pagination.limit)).all())

    return PaginatedResponse(
        items=items,
        total=total,
        limit=pagination.limit,
        offset=pagination.offset,
    )
