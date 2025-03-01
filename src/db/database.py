from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from src.config.base_config import get_db_url

DATABASE_URL = get_db_url()
engine = create_async_engine(DATABASE_URL, echo=True)
Session = async_sessionmaker(bind=engine, expire_on_commit=False)


@asynccontextmanager
async def get_db_session():
    session = Session()
    try:
        yield session
        await session.commit()
    except Exception as e:
        await session.rollback()
        raise e
    finally:
        await session.close()


class ModelBase(DeclarativeBase):
    pass
