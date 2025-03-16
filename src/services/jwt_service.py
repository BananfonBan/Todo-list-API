from typing import Optional

from jose import jwt, JWTError
from datetime import datetime, timedelta, timezone
from src.config.base_config import get_auth_data


class JWTService:
    @staticmethod
    def create_access_token(
        user_id: int, expires_delta: timedelta = timedelta(minutes=30)
    ) -> str:
        """
        Create a new JWT access token for a user.

        :param user_id: int - The ID of the user for whom to create the token
        :param expires_delta: timedelta - Token expiration time (default: 30 minutes)
        :return: str - Encoded JWT token
        """
        data = {"sub": str(user_id), "type": "access"}
        return JWTService._create_token(data, expires_delta)


    @staticmethod
    def create_refresh_token(
        user_id: int, expires_delta: timedelta = timedelta(days=30)
    ) -> str:
        """
        Create a new JWT refresh token for a usr.

        :param user_id: int - The ID of the user for whom to create the token
        :param expires_delta: timedelta - Token expiration time (default: 30 days)
        :return: str - Encoded JWT token
        """
        data = {"sub": str(user_id), "type": "refresh"}
        return JWTService._create_token(data, expires_delta)


    @staticmethod
    def get_expire_time(token: str) -> Optional[datetime]:
        """
        Get the expiration time of a JWT token.

        :param token: str - JWT token to decode
        :return: Optional[datetime] - Token expiration time or None if token is invalid
        """
        payload = JWTService.decode_token(token)
        if payload is None:
            return None

        expire = payload.get("exp")
        expire_time = datetime.fromtimestamp(int(expire), tz=timezone.utc)
        return expire_time


    @staticmethod
    def _create_token(
        data: dict, expires_delta: timedelta = timedelta(minutes=30)
    ) -> str:
        """
        Internal method to create a JWT token with the given data and expiration time.

        :param data: dict - Data to encode in the token
        :param expires_delta: timedelta - Token expiration time (default: 30 minutes)
        :return: str - Encoded JWT token
        """
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + expires_delta
        to_encode.update({"exp": expire})

        auth_data = get_auth_data()

        encode_jwt = jwt.encode(
            to_encode, auth_data["secret_key"], algorithm=auth_data["algorithm"]
        )
        return encode_jwt

    @staticmethod
    def decode_token(token: str) -> Optional[dict]:
        """
        Decode and verify a JWT token.

        :param token: str - JWT token to decode
        :return: Optional[dict] - Decoded token payload or None if token is invalid
        """
        auth_data = get_auth_data()
        try:
            payload = jwt.decode(
                token, auth_data["secret_key"], algorithms=[auth_data["algorithm"]]
            )
            return payload
        except JWTError:
            return None
