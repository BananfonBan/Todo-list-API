from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.base_repo import BaseRepo
from src.models.refresh_token_model import RefreshTokenModel
from src.dto import RefreshTokenDTO, CreateRefreshTokenDTO

from src.config.logging_confing import logging  # noqa


class TokenRepo(BaseRepo):
    model = RefreshTokenModel
    dto = RefreshTokenDTO

    def __init__(self, session: AsyncSession):
        super().__init__(model=RefreshTokenModel, dto=RefreshTokenDTO)

    @classmethod
    async def add_token(
        cls, session: AsyncSession, token: CreateRefreshTokenDTO
    ) -> None:
        """
        Add a refresh token to the database.

        :param session: AsyncSession - SQLAlchemy async session
        :param token: CreateRefreshTokenDTO - Refresh token DTO
        :return: None
        """
        token_instance = RefreshTokenModel(
            token=token.token,
            user_id=token.user_id,
            expires_at=token.expires_at,
        )
        async with session as s:
            s.add(token_instance)
            await s.commit()
        return None

    @classmethod
    async def check_token_exist(
        cls, session: AsyncSession, token: str
    ) -> Optional[RefreshTokenDTO]:
        """
        Find a refresh token by token string.

        :param session: AsyncSession - SQLAlchemy async session
        :param token: str - refresh token
        :return: Optional[RefreshTokenDTO] - Refresh token DTO or None if not found
        """
        async with session as s:
            query = select(cls.model).filter_by(token=token)
            instance = await s.execute(query)
            instance = instance.scalars().first()
        if instance is None:
            return None
        return cls._convert_to_dto(instance, cls.dto)

    @classmethod
    async def update_token(
        cls, session: AsyncSession, old_token: str, new_token: CreateRefreshTokenDTO
    ) -> Optional[RefreshTokenDTO]:
        """
        Update an existing refres htoken to a new token.

        :param session: AsyncSession - SQLAlchemy async session
        :param old_token: str - Refresh token
        :param new_token: CreateRefreshTokenDTO - New refresh token
        :return: Optional[RefreshTokenDTO] - New refresh token or None if old token not found
        """
        async with session as s:
            query = select(cls.model).filter_by(
                token=old_token, user_id=new_token.user_id
            )
            instance = await s.execute(query)
            instance = instance.scalars().first()
            if instance is None:
                return None
            instance.token = new_token.token
            instance.expires_at = new_token.expires_at
            await s.commit()
            await s.refresh(instance=instance)
        return cls._convert_to_dto(instance=instance, dto_class=cls.dto)

    @classmethod
    async def count_tokens_for_user(cls, session: AsyncSession, user_id: int) -> int:
        """
        Count the number of tokens from the user.

        :param: session AsyncSession - SQLAlchemy async session
        :param: user_id int - user ID
        :return: int - The number of tokens by the user
        """
        async with session as s:
            query = select(func.count(cls.model.id)).where(
                cls.model.user_id == user_id,
                cls.model.expires_at > datetime.now(timezone.utc),
            )
            instance = await s.execute(query)
            active_tokens = instance.scalar()

        return active_tokens

    @classmethod
    async def delete_oldest_token(cls, session: AsyncSession, user_id: int) -> None:
        """
        Delete the oldest user refresh token (the one that was created before the rest)

        :param session: AsyncSession - SQLAlchemy async session
        :param user_id: int - User ID
        :return: None
        """
        async with session as s:
            oldest_token = await cls._get_oldest_token(session, user_id)
            if oldest_token is None:
                return None
            await s.delete(oldest_token)
            await s.commit()
        return None

    @classmethod
    async def delete_token(
        cls, session: AsyncSession, token: str, user_id: int
    ) -> None:
        """
        Delete a refresh token.

        :param session: AsyncSession - SQLAlchemy async session
        :param token: str - refresh token
        :param user_id: int - user ID
        :return: None
        """
        async with session as s:
            query = select(cls.model).filter_by(token=token, user_id=user_id)
            instance = await s.execute(query)
            instance = instance.scalars().first()
            if instance is None:
                return None
            await s.delete(instance)
            await s.commit()
        return None

    @classmethod
    async def _get_oldest_token(
        cls, session: AsyncSession, user_id: int
    ) -> Optional[RefreshTokenModel]:
        """
        Return the oldest user refresh token (the one that was created before the rest)

        :param session: AsyncSession - SQLAlchemy async session
        :param user_id: int - User ID
        :return: Optional[RefreshTokenModel] - RefreshTokenModel or None if not found
        """
        async with session as s:
            query = (
                select(cls.model)
                .filter(
                    cls.model.user_id == user_id,
                    cls.model.expires_at > datetime.now(timezone.utc),
                )
                .order_by(cls.model.created_at.asc())
            )
            instance = await s.execute(query)
            oldest_token = instance.scalars().first()
        if oldest_token is None:
            return None
        return oldest_token
