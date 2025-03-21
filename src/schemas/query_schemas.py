from typing import Literal

from pydantic import BaseModel, Field


class FilterParams(BaseModel):
    limit: int = Field(100, gt=0, le=100)
    offset: int = Field(0, ge=0)
    order_by: Literal["created_at", "updated_at", "id"] = "created_at"
    tags: list[str] = []

