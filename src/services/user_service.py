from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories import UserRepo
from src.dto import UserResponseDTO


class UserService:

    @staticmethod
    async def get_user_by_email(
        session: AsyncSession,
        email: str,
    ) -> Optional[UserResponseDTO]:
        """
        Find one user by email and return it as DTO or None.

        :param session: AsyncSession - SQLAlchemy async session
        :param email: str - user email
        :return: Optional[UserResponseDTO] - UserResponseDTO object or None if not found
        """
        return await UserRepo.find_by_email(session, email)
