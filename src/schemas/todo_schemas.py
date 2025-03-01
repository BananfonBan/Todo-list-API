from pydantic import BaseModel

class SToDo(BaseModel):
    id: int
    title: str
    description: str


class SCreateToDo(BaseModel):
    title: str
    description: str


class SToDoList(BaseModel):
    data: list[SToDo]
    offset: int
    limit: int
    total: int
