from datetime import datetime, timedelta

import pytest_asyncio
import pytest
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from fastapi.testclient import TestClient

from src.app import app
from src.db.database import ModelBase, get_db_session
from src.services.auth_service import get_password_hash
from src.models import ToDoModel, UserModel, RefreshTokenModel
from src.config.logging_confing import logging  # noqa


@pytest_asyncio.fixture
async def db_session():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(ModelBase.metadata.create_all)

    session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with session() as s:
        test_data = [
            UserModel(
                name="test_user",
                email="test@example.com",
                password="hashed_password",
            ),
            ToDoModel(
                title="First title",
                description="Default description",
                user_id=1,
            ),
            ToDoModel(
                title="Second title",
                description="Second description",
                user_id=1
            )
        ]
        s: AsyncSession
        s.add_all(test_data)
        await s.commit()

        yield s

    # Delete all tables after tests
    async with engine.begin() as conn:
        await conn.run_sync(ModelBase.metadata.drop_all)


@pytest.fixture
def client(db_session):
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db_session] = override_get_db
    return TestClient(app)


@pytest.fixture
async def test_user(db_session: AsyncSession):
    user = UserModel(
        email="test@example.com",
        name="Test User",
        password=get_password_hash("testpassword"),
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def test_user_token(db_session: AsyncSession):
    token = RefreshTokenModel(
        token="test_token",
        user_id=1,
        expires_at=datetime.now() + timedelta(days=1),
    )
    db_session.add(token)
    await db_session.commit()
    await db_session.refresh(token)
    return token
