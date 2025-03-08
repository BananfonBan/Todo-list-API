from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
import pytest_asyncio


from src.db.database import ModelBase
from src.models import ToDoModel, UserModel
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
