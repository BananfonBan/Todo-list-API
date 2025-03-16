import time
from datetime import datetime, timedelta, timezone

from src.services import JWTService


def test_create_token():
    # Data for token
    data = {"sub": "1"}

    # Create token
    token = JWTService._create_token(data)

    # Check token structure
    assert isinstance(token, str)
    parts = token.split(".")
    assert len(parts) == 3

    # Check token decoding
    decoded_data = JWTService.decode_token(token)
    assert decoded_data is not None
    assert decoded_data["sub"] == data["sub"]

    # Check expiration time
    assert "exp" in decoded_data
    assert decoded_data["exp"] > datetime.now(timezone.utc).timestamp()


def test_create_access_token():
    token = JWTService.create_access_token(1)

    assert isinstance(token, str)
    parts = token.split(".")
    assert len(parts) == 3

    decoded_data = JWTService.decode_token(token)

    assert decoded_data is not None
    assert decoded_data["sub"] == "1"
    assert "exp" in decoded_data
    assert decoded_data["exp"] > datetime.now(timezone.utc).timestamp()


def test_expired_token():
    # Create token with expiration time 1 second
    data = {"sub": "1"}
    token = JWTService._create_token(data, expires_delta=timedelta(seconds=1))

    # Wait
    time.sleep(5)

    # Try to decode token
    decoded_data = JWTService.decode_token(token)
    # Token must be invalid
    assert decoded_data is None
