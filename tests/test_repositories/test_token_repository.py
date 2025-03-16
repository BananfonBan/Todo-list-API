from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import pytest

from src.repositories.token_repo import TokenRepo
from src.models import RefreshTokenModel
from src.dto import CreateRefreshTokenDTO, RefreshTokenDTO
from src.config.logging_confing import logging  # noqa


@pytest.mark.asyncio
async def test_add_token(db_session: AsyncSession):
    token = CreateRefreshTokenDTO(
        token="test_token",
        user_id=1,
        expires_at=datetime.now() + timedelta(days=1),
    )

    await TokenRepo.add_token(db_session, token)

    query = select(RefreshTokenModel).where(RefreshTokenModel.token == "test_token")
    stored_token = (await db_session.execute(query)).scalar_one()

    assert stored_token.token == token.token
    assert stored_token.user_id == token.user_id
    assert stored_token.expires_at == token.expires_at


@pytest.mark.asyncio
async def test_check_token_exist(
    db_session: AsyncSession, test_user_token: RefreshTokenDTO
):
    found_token: RefreshTokenDTO = await TokenRepo.check_token_exist(
        db_session, test_user_token.token
    )

    assert found_token.token == test_user_token.token


@pytest.mark.asyncio
async def test_check_token_not_exist(db_session: AsyncSession):
    found_token: RefreshTokenDTO = await TokenRepo.check_token_exist(
        db_session, "test_token"
    )
    assert found_token is None


@pytest.mark.asyncio
async def test_update_token(db_session: AsyncSession, test_user_token: RefreshTokenDTO):
    new_token = CreateRefreshTokenDTO(
        token="new_token",
        user_id=1,
        expires_at=datetime.now() + timedelta(days=1),
    )

    updated_token = await TokenRepo.update_token(
        db_session, test_user_token.token, new_token
    )

    query = select(RefreshTokenModel).where(RefreshTokenModel.token == "new_token")
    stored_token = (await db_session.execute(query)).scalar_one()

    assert stored_token.token == new_token.token == updated_token.token
    assert stored_token.user_id == new_token.user_id
    assert stored_token.expires_at == new_token.expires_at
    assert stored_token.token != "test_token"


@pytest.mark.asyncio
async def test_update_token_not_exist(db_session: AsyncSession):
    new_token = CreateRefreshTokenDTO(
        token="new_token",
        user_id=1,
        expires_at=datetime.now() + timedelta(days=1),
    )

    not_exist_token = await TokenRepo.update_token(db_session, "test_token", new_token)

    assert not_exist_token is None


@pytest.mark.asyncio
async def test_count_token_for_user(db_session: AsyncSession, test_user_token):
    count = await TokenRepo.count_tokens_for_user(db_session, 1)

    assert count == 1

    second_token = CreateRefreshTokenDTO(
        token="second_token",
        user_id=1,
        expires_at=datetime.now() + timedelta(days=1),
    )

    await TokenRepo.add_token(db_session, second_token)

    count = await TokenRepo.count_tokens_for_user(db_session, 1)

    assert count == 2


@pytest.mark.asyncio
async def test_get_oldest_token_not_exist(db_session: AsyncSession):
    not_exist_token = await TokenRepo._get_oldest_token(session=db_session, user_id=1)

    assert not_exist_token is None


@pytest.mark.asyncio
async def test_get_oldest_token(db_session: AsyncSession, test_user_token):
    new_token = CreateRefreshTokenDTO(
        token="new_token", user_id=1, expires_at=datetime.now() + timedelta(days=1)
    )

    await TokenRepo.add_token(session=db_session, token=new_token)

    oldest_token = await TokenRepo._get_oldest_token(session=db_session, user_id=1)

    assert isinstance(oldest_token, RefreshTokenModel)
    assert oldest_token.token == test_user_token.token


@pytest.mark.asyncio
async def test_delete_oldest_token(db_session: AsyncSession, test_user_token):
    new_token = CreateRefreshTokenDTO(
        token="new_token", user_id=1, expires_at=datetime.now() + timedelta(days=1)
    )

    await TokenRepo.add_token(session=db_session, token=new_token)

    await TokenRepo.delete_oldest_token(session=db_session, user_id=1)

    new_oldest_token = await TokenRepo._get_oldest_token(db_session, 1)

    assert new_oldest_token.token == new_token.token


@pytest.mark.asyncio
async def test_delete_token(db_session: AsyncSession, test_user_token):
    deleted_token = await TokenRepo.delete_token(session=db_session, token=test_user_token.token, user_id=1)

    query = select(RefreshTokenModel).where(RefreshTokenModel.token == "new_token")
    stored_token = (await db_session.execute(query)).one_or_none()

    assert stored_token is None
    assert deleted_token is None


    