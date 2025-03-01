from datetime import datetime

from pydantic import BaseModel


class ToDoDTO(BaseModel):
    id: int
    title: str
    description: str
    created_at: datetime
    updated_at: datetime
    user_id: int

    class Config:
        orm_mod = True
        from_attributes=True

class ToDoUpdateDTO:
    title: str
    description: str
