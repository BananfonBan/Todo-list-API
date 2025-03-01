from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.repositories.base_repo import BaseRepo
from src.models import UserModel
from src.dto import UserResponseDTO, UserCreateDTO


class UserRepo(BaseRepo):
    model = UserModel
    dto = UserResponseDTO

    def __init__(self, session: AsyncSession):
        super().__init__(model=UserModel, dto=UserResponseDTO)

    @classmethod
    async def find_by_email(
        cls, session: AsyncSession, email: str
    ) -> Optional[UserResponseDTO]:
        """
        Find one user by email and return it as DTO or None.

        :param session: AsyncSession - SQLAlchemy async session
        :param email: str - user email
        :return: Optional[UserResponseDTO] - UserResponseDTO object or None if not found
        """
        async with session as s:
            query = select(cls.model).filter_by(email=email)
            instance = await s.execute(query)
        result = cls._convert_to_dto(instance.scalar_one_or_none(), cls.dto)
        return result

    @classmethod
    async def add_user(
        cls, session: AsyncSession, user: UserCreateDTO
    ) -> UserResponseDTO:
        """
        Add a new user to the database and return it as DTO.

        :param session: AsyncSession - SQLAlchemy async session
        :param user: UserCreateDTO - data for creating a new user
        :return: UserResponseDTO - created UserResponseDTO object
        """
        user_data = UserModel(**user.model_dump())
        async with session as s:
            s.add(user_data)
            await s.commit()
            await s.refresh(user_data)
        return cls._convert_to_dto(user_data, cls.dto)

    @classmethod
    async def get_password_hash(cls, session: AsyncSession, email: str) -> str | None:
        """
        Get the password hash for a user by email.

        :param session: AsyncSession - SQLAlchemy async session
        :param email: str - user email
        :return: Optional[str] - password hash or None if not found
        """
        async with session as s:
            query = select(cls.model).filter_by(email=email)
            instance = await s.execute(query)
        result = instance.scalar_one_or_none()
        if result is None:
            return None
        return result.password
