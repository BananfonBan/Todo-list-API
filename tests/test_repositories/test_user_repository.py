from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
import pytest


from src.repositories import UserRepo
from src.dto import UserResponseDTO, UserCreateDTO
from src.config.logging_confing import logging  # noqa


@pytest.mark.asyncio
async def test_find_by_email(db_session: AsyncSession):
    user_dto: UserResponseDTO = await UserRepo.find_by_email(db_session, "test@example.com")

    assert isinstance(user_dto, UserResponseDTO)
    assert user_dto.id == 1
    assert user_dto.name == "test_user"
    assert user_dto.email == "test@example.com"

    none_user = await UserRepo.find_by_email(db_session, 42)

    assert none_user is None


@pytest.mark.asyncio
async def test_add_user(db_session: AsyncSession):
    user_data = UserCreateDTO(
        name="Mike",
        email="mike@test.com",
        password="mike1999",
    )
    new_user = await UserRepo.add_user(db_session, user_data)

    # Check that DTO has returned
    assert isinstance(new_user, UserResponseDTO)
    assert new_user.name == "Mike"
    assert new_user.email == "mike@test.com"
    assert new_user.id == 2

    # Check that the data is really saved in the database
    query = text("SELECT * FROM users WHERE id = :id")
    result = await db_session.execute(query, {"id": new_user.id})

    stored_user = result.mappings().one()  # Get first record as dict

    # Check data
    assert stored_user["name"] == "Mike"
    assert stored_user["email"] == "mike@test.com"
    assert stored_user["id"] == 2


@pytest.mark.asyncio
async def test_get_passowrd_hash(db_session):
    hashed_password = await UserRepo.get_password_hash(db_session, "test@example.com")

    assert hashed_password == "hashed_password"

    none_password = await UserRepo.get_password_hash(db_session, "none@email.com")
    
    assert none_password is None
