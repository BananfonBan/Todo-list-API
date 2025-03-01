from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.base_repo import BaseRepo
from src.models.todo_model import ToDoModel
from src.dto import ToDoDTO, ToDoUpdateDTO

from src.config.logging_confing import logging  # noqa


class TodoRepo(BaseRepo):
    model = ToDoModel
    dto = ToDoDTO

    def __init__(self, session: AsyncSession):
        super().__init__(model=ToDoModel, dto=ToDoDTO)

    @classmethod
    async def find_all_todos_by_user_id(
        cls,
        session: AsyncSession,
        user_id: int,
        offset: int = 0,
        limit: int = 10,
    ) -> List[ToDoDTO]:
        """
        Find all todos for a specific user with pagination.

        :param session: AsyncSession - SQLAlchemy async session
        :param user_id: int - user ID
        :param offset: int - pagination offset
        :param limit: int - pagination limit
        :return: List[ToDoDTO] - list of ToDoDTO objects
        """
        async with session as s:
            query = (
                select(cls.model).filter_by(user_id=user_id).offset(offset).limit(limit)
            )
            instance = await s.execute(query)
        result = cls._convert_to_dto_list(instance.scalars().all(), cls.dto)
        return result

    @classmethod
    async def create_todo(
        cls,
        session: AsyncSession,
        user_id: int,
        title: str,
        description: str,
    ) -> ToDoDTO:
        """
        Create a new todo for a specific user.

        :param session: AsyncSession - SQLAlchemy async session
        :param user_id: int - user ID
        :param title: str - title of the todo
        :param description: str - description of the todo
        :return: ToDoDTO - created ToDoDTO object
        """
        todo = ToDoModel(title=title, description=description, user_id=user_id)
        async with session as s:
            s.add(todo)
            await s.commit()
            await s.refresh(todo)
        return cls._convert_to_dto(todo, cls.dto)

    @classmethod
    async def update_todo(
        cls, session: AsyncSession, todo_id: int, new_todo_data: ToDoUpdateDTO
    ):
        """
        Update an existing todo with new data.

        :param session: AsyncSession - SQLAlchemy async session
        :param todo_id: int - todo ID
        :param new_todo_data: ToDoUpdateDTO - new data for the todo
        :return: Optional[ToDoDTO] - updated ToDoDTO object or None if not found
        """
        async with session as s:
            todo = await cls._find_by_id(session=s, id=todo_id)
            if not todo:
                return None
            for key, value in new_todo_data.dict(exclude_unset=True).items():
                setattr(todo, key, value)
            s.add(todo)
            await s.commit()
            await s.refresh(todo)
        return cls._convert_to_dto(todo, cls.dto)

    @classmethod
    async def get_todo_owner_id(
        cls, session: AsyncSession, todo_id: int
    ) -> Optional[int]:
        """
        Get the owner ID of a specific todo.

        :param session: AsyncSession - SQLAlchemy async session
        :param todo_id: int - todo ID
        :return: Optional[int] - user ID or None if not found
        """
        async with session as s:
            query = select(cls.model).filter_by(id=todo_id)
            instance = await s.execute(query)
        todo = cls._convert_to_dto(instance.scalars().one_or_none(), cls.dto)
        return todo.user_id
