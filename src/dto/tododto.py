from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ToDoDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str
    created_at: datetime
    updated_at: datetime
    user_id: int


class ToDoUpdateDTO:
    title: str
    description: str
