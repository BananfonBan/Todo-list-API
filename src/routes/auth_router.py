from typing import Optional, Annotated, Literal

from fastapi import APIRouter, Response, Depends, Body

from src.db import get_db_session
from src.config.base_config import get_auth_method
from src.services import AuthService, UserService
from src.dto import UserCreateDTO, UserLoginDTO
from src.schemas import SUser, SUserRegister, SUserLogin, SJWTToken
from src.routes.dependencies import get_current_user
from src.exceptions import routers_exceptions

from src.config.logging_confing import logging  # noqa


router = APIRouter(prefix="/auth", tags=["Auth"])


auth_method: Literal["cookie", "header"] = get_auth_method()

# NOTE HTTPexception should only be at the router level


@router.post("/register")
async def register_user(user_data: Annotated[SUserRegister, Body()]) -> SUser:
    user = await UserService.get_user_by_email(
        session=get_db_session(), email=user_data.email
    )
    if user:
        raise routers_exceptions.UserAlreadyExistError

    user_data = SUserRegister.model_dump(user_data)
    user = await AuthService.create_user(
        session=get_db_session(), user=UserCreateDTO(**user_data)
    )

    return SUser.model_dump(user)


@router.post("/login")
async def login_user(response: Response, user_data: SUserLogin) -> Optional[SJWTToken]:
    user_data = SUserLogin.model_dump(user_data)

    token = await AuthService.login_user(
        session=get_db_session(), user=UserLoginDTO(**user_data)
    )

    if token is None:
        raise routers_exceptions.WrongLoginDataError

    if auth_method == "cookie":
        response.set_cookie(
            key="users_access_token",
            value=token.access_token,
            httponly=True,
            secure=True,
        )

    return SJWTToken(access_token=token.access_token, refresh_token=None)


@router.get("/me")
async def get_me(user: SUser = Depends(get_current_user)) -> SUser:
    return SUser.model_dump(user)


# FIXME Add logout system for "header" auth method
@router.post("/logout")
async def logout(response: Response):
    if auth_method == "cookie":
        response.delete_cookie(key="users_access_token", httponly=True)

    return {"message": "Successfully logged out"}
