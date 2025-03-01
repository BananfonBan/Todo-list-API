from typing import TypeVar, Type, Optional, List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.config.logging_confing import logging  # noqa

# Abstract type for SQLAlchemy model
ModelType = TypeVar("ModelType")
# Abstract type for DTO
DTOType = TypeVar("DTOType")


class BaseRepo:
    model = None
    dto = None

    def __init__(self, model: Type[ModelType], dto: Type[DTOType]):
        self.model = model
        self.dto = dto

    @classmethod
    async def find_by_id(cls, session: AsyncSession, id: int) -> Optional[DTOType]:
        """
        Find one record by ID and return it as a DTO.

        :param session: AsyncSession - SQLAlchemy async session
        :param id: int - record ID
        :return: Optional[DTOType] - DTO object or None if not found
        """
        async with session as s:
            query = select(cls.model).filter_by(id=id)
            instance = await s.execute(query)
        result = cls._convert_to_dto(instance.scalar_one_or_none(), cls.dto)
        return result

    @classmethod
    async def find_one_or_none(
        cls,
        session: AsyncSession,
        **filter_params: dict,
    ) -> Optional[DTOType]:
        """
        Find one record by filter and return it as a DTO.

        :param session: AsyncSession - SQLAlchemy async session
        :param filter_params: dict - filter parameters
        :return: Optional[DTOType] - DTO object or None if not found
        """
        async with session as s:
            query = select(cls.model).filter_by(**filter_params)
            instance = await s.execute(query)
        result = cls._convert_to_dto(instance.scalar_one_or_none(), cls.dto)
        return result

    @classmethod
    async def find_all(
        cls,
        session: AsyncSession,
        offset: int = 0,
        limit: int = 10,
    ) -> List[DTOType]:
        """
        Find all records with pagination and return them as a list of DTOs.

        :param session: AsyncSession - SQLAlchemy async session
        :param offset: int - pagination offset
        :param limit: int - pagination limit
        :return: List[DTOType] - list of DTO objects
        """
        async with session as s:
            query = select(cls.model).offset(offset).limit(limit)
            instance = await s.execute(query)
        result = cls._convert_to_dto_list(instance.scalars().all(), cls.dto)
        return result

    @classmethod
    async def delete_by_id(cls, session: AsyncSession, id: int) -> None:
        """
        Delete a record by ID.

        :param session: AsyncSession - SQLAlchemy async session
        :param id: int - record ID
        :return: None
        """
        async with session as s:
            record = await cls._find_by_id(session=s, id=id)
            await s.delete(record)
            await s.commit()
        return None

    @classmethod
    async def _find_by_id(cls, session: AsyncSession, id: int) -> ModelType:
        """
        Helper method to find a record by ID.

        :param session: AsyncSession - SQLAlchemy async session
        :param id: int - record ID
        :return: ModelType - SQLAlchemy model or None if not found
        """
        async with session as s:
            query = select(cls.model).filter_by(id=id)
            instance = await s.execute(query)
        return instance.scalars().one_or_none()

    @staticmethod
    def _convert_to_dto(
        instance: ModelType, dto_class: Type[DTOType]
    ) -> Optional[DTOType]:
        """
        Convert SQLAlchemy model instance to a DTO.

        :param instance: ModelType
        :param dto_class: Type[DTOType]
        :return: DTOType
        """
        if instance is None:
            return None
        # Use Pydantic's from_orm for conversion
        return dto_class.from_orm(instance)

    @staticmethod
    def _convert_to_dto_list(
        instance_list: List[ModelType], dto_class: Type[DTOType]
    ) -> List[DTOType]:
        """
        Convert SQLAlchemy models in instance_List to DTO.

        :param instance_List: List[ModelType]
        :param dto_class: Type[DTOType]
        :return: List[DTOType]
        """
        if instance_list is None:
            return []
        # Use Pydantic's from_orm for conversion
        return [dto_class.from_orm(i) for i in instance_list]
