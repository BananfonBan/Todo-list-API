from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession
import pytest


from src.repositories.todo_repo import TodoRepo
from src.models import ToDoModel
from src.dto import ToDoDTO, ToDoUpdateDTO
from src.config.logging_confing import logging  # noqa


@pytest.mark.asyncio
async def test_find_by_id(db_session: AsyncSession):
    first_todo: ToDoModel = await TodoRepo._find_by_id(db_session, 1)

    assert isinstance(first_todo, ToDoModel)

    query = select(ToDoModel).where(ToDoModel.id == 1)
    stored_todo = (await db_session.execute(query)).scalar_one()

    assert stored_todo.id == first_todo.id
    assert stored_todo.title == first_todo.title
    assert stored_todo.description == first_todo.description
    assert stored_todo.user_id == first_todo.user_id

    none_todo = await TodoRepo._find_by_id(db_session, 42)

    assert none_todo is None


@pytest.mark.asyncio
async def test_find_by_id_as_dto(db_session: AsyncSession):
    first_todo_dto: ToDoDTO = await TodoRepo.find_by_id(db_session, 1)

    assert isinstance(first_todo_dto, ToDoDTO)
    assert first_todo_dto.title == "First title"
    assert first_todo_dto.description == "Default description"

    none_todo = await TodoRepo.find_by_id(db_session, 42)

    assert none_todo is None


@pytest.mark.asyncio
async def test_find_all(db_session: AsyncSession):
    todo_list: list[ToDoDTO] = await TodoRepo.find_all(db_session)

    assert len(todo_list) == 2

    for todo in todo_list:
        assert isinstance(todo, ToDoDTO)

    assert todo_list[0].title == "First title"
    assert todo_list[0].description == "Default description"
    assert todo_list[1].title == "Second title"
    assert todo_list[1].description == "Second description"


@pytest.mark.asyncio
async def test_delete_by_id(db_session):
    await TodoRepo.delete_by_id(db_session, 1)

    none_todo = await TodoRepo.find_by_id(db_session, 1)
    assert none_todo is None


@pytest.mark.asyncio
async def test_find_all_by_user_id(db_session: AsyncSession):
    todo_list: list[ToDoDTO] = await TodoRepo.find_all_todos_by_user_id(db_session, 1)

    assert len(todo_list) == 2

    for todo in todo_list:
        assert isinstance(todo, ToDoDTO)

    assert todo_list[0].title == "First title"
    assert todo_list[0].description == "Default description"
    assert todo_list[1].title == "Second title"
    assert todo_list[1].description == "Second description"


@pytest.mark.asyncio
async def test_create_todo(db_session: AsyncSession):
    result_dto = await TodoRepo.create_todo(
        session=db_session, user_id=1, title="Test Todo", description="description"
    )

    # Check that DTO has returned
    assert isinstance(result_dto, ToDoDTO)
    assert result_dto.title == "Test Todo"

    # Check that the data is really saved in the database
    query = text("SELECT * FROM todos WHERE id = :id")
    result = await db_session.execute(query, {"id": result_dto.id})

    stored_todo = result.mappings().one()  # Get first record as dict

    # Check data
    assert stored_todo["title"] == "Test Todo"
    assert stored_todo["description"] == "description"
    assert stored_todo["user_id"] == 1


@pytest.mark.asyncio
async def test_update_todo(db_session: AsyncSession):
    dict_data = {"title": "Absolutly new title", "description": "New Description"}
    new_data = ToDoUpdateDTO.model_validate(dict_data)
    updated_todo = await TodoRepo.update_todo(
        session=db_session, todo_id=1, new_todo_data=new_data
    )
    assert isinstance(updated_todo, ToDoDTO)
    assert updated_todo.title == "Absolutly new title"
    assert updated_todo.description == "New Description"

    query = text("SELECT * FROM todos WHERE id = :id")
    result = await db_session.execute(query, {"id": 1})

    stored_todo = result.mappings().one()

    assert stored_todo["title"] == "Absolutly new title"
    assert stored_todo["description"] == "New Description"
    assert stored_todo["user_id"] == 1

    none_todo = await TodoRepo.update_todo(db_session, 42, new_data)

    assert none_todo is None


@pytest.mark.asyncio
async def test_get_todo_ower_id(db_session: AsyncSession):
    user_id = await TodoRepo.get_todo_owner_id(db_session, 1)

    assert user_id == 1
