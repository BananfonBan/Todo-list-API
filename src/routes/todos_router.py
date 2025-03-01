from typing import Optional, Annotated

from fastapi import APIRouter, status, Query, Depends

from src.db import get_db_session
from src.services import ToDoService
from src.exceptions import routers_exceptions
from src.schemas import SToDoList, SCreateToDo, SToDo, FilterParams, SUser
from src.routes.dependencies import get_current_user

from src.config.logging_confing import logging  # noqa


router = APIRouter(prefix="/todos", tags=["To-do list"])


@router.get("")
async def get_todos(
    filter_query: Annotated[FilterParams, Query()],
    user: SUser = Depends(get_current_user),
) -> SToDoList:
    todos = await ToDoService.get_all_todos(
        session=get_db_session(),
        offset=filter_query.offset,
        limit=filter_query.limit,
        order_by=filter_query.order_by,
    )
    data = [SToDo.model_dump(todo) for todo in todos]
    return SToDoList(
        data=data, offset=filter_query.offset, limit=filter_query.limit, total=len(data)
    )


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_todo(
    todo: SCreateToDo,
    user: SUser = Depends(get_current_user),
) -> SToDo:
    new_todo = await ToDoService.create_todo(
        session=get_db_session(),
        user_id=user.id,
        title=todo.title,
        description=todo.description,
    )
    return SToDo.model_dump(new_todo)


@router.get("/my")
async def get_my_todos(
    filter_query: Annotated[FilterParams, Query()],
    user: SUser = Depends(get_current_user),
) -> SToDoList:
    todos = await ToDoService.get_all_todos_by_user_id(
        session=get_db_session(),
        user_id=user.id,
        offset=filter_query.offset,
        limit=filter_query.limit,
        order_by=filter_query.order_by,
    )
    data = [SToDo.model_dump(todo) for todo in todos]
    return SToDoList(
        data=data, offset=filter_query.offset, limit=filter_query.limit, total=len(data)
    )


@router.get("/{id}")
async def get_todo_by_id(id: int) -> Optional[SToDo]:
    todo = await ToDoService.get_todo_by_id(session=get_db_session(), todo_id=id)

    if not todo:
        raise routers_exceptions.NotFoundToDo

    return SToDo.model_dump(todo)


@router.put("/{id}")
async def update_todo_by_id(
    id: int, new_todo_data: SCreateToDo, user: SUser = Depends(get_current_user)
) -> SToDo:
    todo = await ToDoService.get_todo_by_id(session=get_db_session(), todo_id=id)

    if not todo:
        raise routers_exceptions.NotFoundToDo

    if not await ToDoService.check_todo_owner(
        session=get_db_session(), user_id=user.id, todo_id=todo.id
    ):
        raise routers_exceptions.ForbiddenError

    new_todo = await ToDoService.update_todo(
        session=get_db_session(), todo_id=id, new_todo=new_todo_data
    )

    return SToDo.model_dump(new_todo)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo_by_id(id: int, user: SUser = Depends(get_current_user)):
    todo = await ToDoService.get_todo_by_id(session=get_db_session(), todo_id=id)

    if not todo:
        raise routers_exceptions.NotFoundToDo

    if not await ToDoService.check_todo_owner(
        session=get_db_session(), user_id=user.id, todo_id=todo.id
    ):
        raise routers_exceptions.ForbiddenError

    await ToDoService.delete_todo(session=get_db_session(), todo_id=id)
    return None
