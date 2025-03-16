from fastapi import Request, Depends, Security
from fastapi.security.api_key import APIKeyHeader

from src.config.base_config import get_auth_method
from src.db import get_db_session
from src.exceptions import services_exceptions, routers_exceptions
from src.services import AuthService
from src.schemas import SUser

from src.config.logging_confing import logging  # noqa


token_key = APIKeyHeader(name="Authorization")


async def get_access_token_from_cookie(request: Request):
    token = request.cookies.get("users_access_token")
    if not token:
        raise routers_exceptions.UnauthorizedError
    return token


async def get_access_token_from_headers(auth_key: str = Security(token_key)):
    if not auth_key:
        raise routers_exceptions.UnauthorizedError

    scheme, _, token = auth_key.partition(" ")
    if scheme.lower() != "bearer":
        raise routers_exceptions.InvalidAuthHeaderFormat

    return token


def get_current_auth_method():
    auth_method = get_auth_method()

    if auth_method == "cookie":
        return get_access_token_from_cookie
    if auth_method == "header":
        return get_access_token_from_headers
    else:
        raise ValueError("Invalid AUTH_METHOD. Use 'header' or 'cookie'.")

get_access_token = get_current_auth_method()


async def get_refresh_token(request: Request) -> str:
    token = request.cookies.get("users_refresh_token")
    if not token:
        raise routers_exceptions.UnauthorizedError
    return token


async def get_current_user(token: str = Depends(get_access_token)) -> SUser:
    try:
        user = await AuthService.get_current_user(session=get_db_session(), token=token)

    except services_exceptions.NotValidTokenError:
        raise routers_exceptions.InvalidToken

    except services_exceptions.ExpiredSignatureTokenError:
        raise routers_exceptions.ExpiredToken

    except services_exceptions.NotFoundTokenError:
        raise routers_exceptions.NotFoundUser

    if user is None:
        raise routers_exceptions.NotFoundUser

    return user
