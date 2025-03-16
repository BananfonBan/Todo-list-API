from typing import Literal

from pydantic import SecretStr, ConfigDict, Field
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    model_config = ConfigDict(env_file=".env", env_file_encoding="utf-8")

    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASS: SecretStr
    DB_NAME: str
    SECRET_KEY: SecretStr
    ALGORITHM: str
    AUTH_METHOD: Literal["header", "cookie"]
    MAX_ACTIVE_SESSIONS: int = Field(ge=1)


settings = Settings()

def get_db_url() -> str:
    return (
        f"postgresql+asyncpg://{settings.DB_USER}:{settings.DB_PASS.get_secret_value()}@"
        f"{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
    )

def get_auth_data() -> dict[Literal["secret_key", "algorithm"], str]:
    return {"secret_key": settings.SECRET_KEY.get_secret_value(), "algorithm": settings.ALGORITHM}

def get_auth_method() -> Literal["header", "cookie"]:
    return settings.AUTH_METHOD

def get_max_active_sessions() -> int:
    return settings.MAX_ACTIVE_SESSIONS