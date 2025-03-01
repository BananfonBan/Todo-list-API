from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from passlib.context import CryptContext

from src.repositories import UserRepo
from src.services.jwt_service import JWTService
from src.exceptions import services_exceptions
from src.dto import UserResponseDTO, UserCreateDTO, UserLoginDTO, TokenDTO

from src.config.logging_confing import logging  # noqa


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    """
    Generate a hash for the given password.

    :param password: str - Plain text password to hash
    :return: str - Hashed password
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against a hashed password.

    :param plain_password: str - Plain text password to verify
    :param hashed_password: str - Hashed password to compare against
    :return: bool - True if passwords match, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)


class AuthService:
    @staticmethod
    async def create_user(
        session: AsyncSession, user: UserCreateDTO
    ) -> UserResponseDTO:
        """
        Create a new user with a hashed password.

        :param session: AsyncSession - SQLAlchemy async session
        :param user: UserCreateDTO - User DTO containing registration data
        :return: UserResponseDTO - Created user DTO
        """
        user.password = get_password_hash(user.password)
        return await UserRepo.add_user(session, user)

    @staticmethod
    async def login_user(
        session: AsyncSession, user: UserLoginDTO
    ) -> Optional[TokenDTO]:
        """
        Authenticate a user and generate an access token.

        :param session: AsyncSession - SQLAlchemy async session
        :param user: UserLoginDTO - User credentials for login
        :return: Optional[TokenDTO] - Token DTO if authentication successful, None otherwise
        """
        async with session as s:
            password_hash = await UserRepo.get_password_hash(
                session=s, email=user.email
            )

            if not password_hash or not verify_password(user.password, password_hash):
                return None

            current_user = await UserRepo.find_by_email(session=s, email=user.email)

        token = JWTService.create_access_token(current_user.id)
        return TokenDTO(access_token=token, token_type="bearer")

    @staticmethod
    async def get_current_user(
        session: AsyncSession, token: str
    ) -> Optional[UserResponseDTO]:
        """
        Get the current authenticated user from a JWT token.

        :param session: AsyncSession - SQLAlchemy async session
        :param token: str - JWT token to validate and decode
        :return: Optional[UserResponseDTO] - User DTO if token is valid
        :raises:
            NotValidTokenError: If the token is invalid

            ExpiredSignatureTokenError: If the token has expired

            NotFoundTokenError: If user ID is not found in token
        """
        payload = JWTService.decode_token(token)

        if payload is None:
            raise services_exceptions.NotValidTokenError("Invalid token")

        expire = payload.get("exp")
        expire_time = datetime.fromtimestamp(int(expire), tz=timezone.utc)
        if (not expire) or (expire_time < datetime.now(timezone.utc)):
            raise services_exceptions.ExpiredSignatureTokenError("Token is expired")

        user_id = payload.get("sub")
        if not user_id:
            return services_exceptions.NotFoundTokenError("User ID not found")

        user = await UserRepo.find_by_id(session, int(user_id))
        return user
