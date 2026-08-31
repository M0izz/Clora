from typing import Generic, TypeVar
from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")


class ErrorResponse(BaseModel):
    detail: str
    error_code: str | None = None


class MessageResponse(BaseModel):
    message: str
    success: bool = True


class PaginationMeta(BaseModel):
    total: int
    page: int
    page_size: int
    total_pages: int


class PaginatedResponse(BaseModel, Generic[T]):
    items: list[T]
    meta: PaginationMeta

    model_config = ConfigDict(from_attributes=True)
