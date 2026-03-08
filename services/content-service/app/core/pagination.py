from typing import Generic, TypeVar, List
from fastapi import Query
from pydantic import BaseModel
from app.core.config import settings

T = TypeVar("T")

class PaginationParams:
    def __init__(
        self,
        page: int = Query(1, ge=1, description="Page number"),
        page_size: int = Query(
            settings.page_size_default,
            ge=1,
            le=settings.page_size_max,
            description="Items per page",
        ),
    ):
        self.page = page
        self.page_size = page_size
        self.offset = (page - 1) * page_size

class PaginatedResponse(BaseModel, Generic[T]):
    total: int
    page: int
    page_size: int
    total_pages: int
    items: List[T]

    model_config = {"from_attributes": True}

    @classmethod
    def create(cls, items: List[T], total: int, page: int, page_size: int):
        return cls(
            total=total,
            page=page,
            page_size=page_size,
            total_pages=(total + page_size - 1) // page_size if page_size > 0 else 0,
            items=items,
        )
