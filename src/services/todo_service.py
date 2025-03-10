from typing import List, Optional, Literal

from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.todo_repo import TodoRepo
from src.dto import ToDoDTO, ToDoUpdateDTO
from src.services.common_func import sort_dto_list_order_by

from src.config.logging_confing import logging # noqa


class ToDoService:
    @staticmethod
    async def get_todo_by_id(session: AsyncSession, todo_id: int) -> Optional[ToDoDTO]:
        """
        Get a todo item by its ID.

        :param session: AsyncSession - SQLAlchemy async session
        :param todo_id: int - ID of the todo item to retrieve
        :return: Optional[ToDoDTO] - Todo item DTO or None if not found
        """
        return await TodoRepo.find_by_id(session, id=todo_id)

    @staticmethod
    async def get_all_todos(
        session: AsyncSession,
        offset: int = 0,
        limit: int = 10,
        order_by: Literal["created_at", "updated_at", "id"] = "id",
    ) -> List[ToDoDTO]:
        """
        Get all todo items with pagination and sorting.

        :param session: AsyncSession - SQLAlchemy async session
        :param offset: int - Number of records to skip (default: 0)
        :param limit: int - Maximum number of records to return (default: 10)
        :param order_by: str - Field to sort by (created_at/updated_at/id, default: id)
        :return: List[ToDoDTO] - List of todo item DTOs
        """
        todos = await TodoRepo.find_all(session, offset=offset, limit=limit)
        return sort_dto_list_order_by(dto=ToDoDTO, dto_list=todos, order_by=order_by)

    @staticmethod
    async def get_all_todos_by_user_id(
        session: AsyncSession,
        user_id: int,
        offset: int = 0,
        limit: int = 10,
        order_by: Literal["created_at", "updated_at", "id"] = "id",
    ) -> List[ToDoDTO]:
        """
        Get all todo items for a specific user with pagination and sorting.

        :param session: AsyncSession - SQLAlchemy async session
        :param user_id: int - ID of the user whose todos to retrieve
        :param offset: int - Number of records to skip (default: 0)
        :param limit: int - Maximum number of records to return (default: 10)
        :param order_by: str - Field to sort by (created_at/updated_at/id, default: id)
        :return: List[ToDoDTO] - List of todo item DTOs
        """
        todos = await TodoRepo.find_all_todos_by_user_id(
            session=session, user_id=user_id, offset=offset, limit=limit
        )

        return sort_dto_list_order_by(dto=ToDoDTO, dto_list=todos, order_by=order_by)

    @staticmethod
    async def create_todo(
        session: AsyncSession,
        user_id: int,
        title: str,
        description: str,
    ) -> ToDoDTO:
        """
        Create a new todo item.

        :param session: AsyncSession - SQLAlchemy async session
        :param user_id: int - ID of the user creating the todo
        :param title: str - Title of the todo item
        :param description: str - Description of the todo item
        :return: ToDoDTO - Created todo item DTO
        """
        todo = await TodoRepo.create_todo(
            session=session, user_id=user_id, title=title, description=description
        )
        return todo

    @staticmethod
    async def update_todo(
        session: AsyncSession,
        todo_id: int,
        new_todo: ToDoUpdateDTO,
    ) -> ToDoDTO:
        """
        Update an existing todo item.

        :param session: AsyncSession - SQLAlchemy async session
        :param todo_id: int - ID of the todo item to update
        :param new_todo: ToDoUpdateDTO - New data for the todo item
        :return: ToDoDTO - Updated todo item DTO
        """
        todo = await TodoRepo.update_todo(
            session=session, todo_id=todo_id, new_todo_data=new_todo
        )
        return todo

    @staticmethod
    async def delete_todo(session: AsyncSession, todo_id: int) -> None:
        """
        Delete a todo item by its ID.

        :param session: AsyncSession - SQLAlchemy async session
        :param todo_id: int - ID of the todo item to delete
        :return: None
        """
        await TodoRepo.delete_by_id(session=session, id=todo_id)

    @staticmethod
    async def check_todo_owner(
        session: AsyncSession, user_id: int, todo_id: int
    ) -> bool:
        """
        Check if a user is the owner of a todo item.

        :param session: AsyncSession - SQLAlchemy async session
        :param user_id: int - ID of the user to check
        :param todo_id: int - ID of the todo item to check
        :return: bool - True if the user is the owner, False otherwise
        """
        owner_id = await TodoRepo.get_todo_owner_id(session=session, todo_id=todo_id)
        return owner_id == user_id
