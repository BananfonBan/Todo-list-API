from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock

import pytest
from src.dto import UserLoginDTO, TokenDTO, UserResponseDTO
from src.services.auth_service import AuthService, get_password_hash, verify_password
from src.services.jwt_service import JWTService
from src.models import UserModel
from src.exceptions import services_exceptions


def test_get_password_hash():
    password = "test_password"
    hashed_password = get_password_hash(password)

    assert isinstance(hashed_password, str)
    assert len(hashed_password) > 0
    assert hashed_password != password


def test_verify_password():
    password = "test_password"
    hashed_password = get_password_hash(password)
    assert verify_password(password, hashed_password)

    assert not verify_password("wrong_password", hashed_password)


@pytest.mark.asyncio
async def test_login_user_success(mocker):
    # Preperation of mocks
    mock_session = AsyncMock()
    user_email = "test@example.com"
    user_password = "secure_password"
    user_name = "Test User"
    password_hash = get_password_hash("secure_password")
    user_id = 1

    # Mocking repository methods
    mocker.patch(
        "src.repositories.user_repo.UserRepo.get_password_hash",
        new=AsyncMock(return_value=password_hash),
    )
    mocker.patch(
        "src.repositories.user_repo.UserRepo.find_by_email",
        new=AsyncMock(
            return_value=UserResponseDTO(id=user_id, email=user_email, name=user_name)
        ),
    )

    user_dto = UserLoginDTO(email=user_email, password=user_password)

    result = await AuthService.login_user(mock_session, user_dto)

    assert isinstance(result, TokenDTO)
    assert result.token_type == "bearer"
    assert "access_token" in result.model_dump()


@pytest.mark.asyncio
async def test_login_user_invalid_password(mocker):
    # Preperation of mocks
    mock_session = AsyncMock()
    user_email = "test@example.com"
    user_password = "wrong_password"
    password_hash = get_password_hash("defautl_password")

    # Mocking repository methods
    mocker.patch(
        "src.repositories.user_repo.UserRepo.get_password_hash",
        new=AsyncMock(return_value=password_hash),
    )
    mocker.patch(
        "src.repositories.user_repo.UserRepo.find_by_email",
        new=AsyncMock(return_value=None),
    )

    user_dto = UserLoginDTO(email=user_email, password=user_password)

    result = await AuthService.login_user(mock_session, user_dto)

    assert result is None


@pytest.mark.asyncio
async def test_login_user_user_not_found(mocker):
    # Preperation of mocks
    mock_session = AsyncMock()
    user_email = "nonexistent@example.com"
    user_password = "secure_password"

    # Mocking repository methods
    mocker.patch(
        "src.repositories.user_repo.UserRepo.get_password_hash",
        new=AsyncMock(return_value=None),
    )
    mocker.patch(
        "src.repositories.user_repo.UserRepo.find_by_email",
        new=AsyncMock(return_value=None),
    )

    user_dto = UserLoginDTO(email=user_email, password=user_password)

    result = await AuthService.login_user(mock_session, user_dto)

    assert result is None


@pytest.mark.asyncio
async def test_login_user_full_integration(db_session):
    # Add a test user to the database
    async with db_session as session:
        test_user = UserModel(
            email="integration@example.com",
            name="Integration User",
            password=get_password_hash("secure_password"),
        )
        session.add(test_user)
        await session.commit()
        await session.refresh(test_user)

    user_dto = UserLoginDTO(email="integration@example.com", password="secure_password")

    result = await AuthService.login_user(db_session, user_dto)

    assert isinstance(result, TokenDTO)
    assert result.token_type == "bearer"
    assert "access_token" in result.model_dump()

    decoded_payload = JWTService.decode_token(result.access_token)
    assert decoded_payload["sub"] == str(test_user.id)


@pytest.mark.asyncio
async def test_get_current_user_success(mocker):
    mock_session = AsyncMock()
    user_id = 1
    test_user = UserResponseDTO(id=user_id, email="test@example.com", name="Test User")
    future_time = int((datetime.now(timezone.utc) + timedelta(hours=1)).timestamp())

    # Mock JWT decode
    mocker.patch(
        "src.services.jwt_service.JWTService.decode_token",
        return_value={"sub": str(user_id), "exp": future_time},
    )

    # Mock user repository
    mocker.patch(
        "src.repositories.user_repo.UserRepo.find_by_id",
        new=AsyncMock(return_value=test_user),
    )

    result = await AuthService.get_current_user(mock_session, "valid_token")
    assert isinstance(result, UserResponseDTO)
    assert result.id == user_id


@pytest.mark.asyncio
async def test_get_current_user_invalid_token(mocker):
    mock_session = AsyncMock()

    # Mock JWT decode returning None
    mocker.patch("src.services.jwt_service.JWTService.decode_token", return_value=None)

    with pytest.raises(services_exceptions.NotValidTokenError) as exc_info:
        await AuthService.get_current_user(mock_session, "invalid_token")
    assert str(exc_info.value) == "Invalid token"


@pytest.mark.asyncio
async def test_get_current_user_expired_token(mocker):
    mock_session = AsyncMock()
    expired_time = int((datetime.now(timezone.utc) - timedelta(hours=1)).timestamp())

    # Mock JWT decode returning expired payload
    mocker.patch(
        "src.services.jwt_service.JWTService.decode_token",
        return_value={"sub": "1", "exp": expired_time},
    )

    with pytest.raises(services_exceptions.ExpiredSignatureTokenError) as exc_info:
        await AuthService.get_current_user(mock_session, "expired_token")
    assert str(exc_info.value) == "Token is expired"


@pytest.mark.asyncio
async def test_get_current_user_missing_user_id(mocker):
    mock_session = AsyncMock()
    future_time = int((datetime.now(timezone.utc) + timedelta(hours=1)).timestamp())

    # Mock JWT decode returning payload without sub
    mocker.patch(
        "src.services.jwt_service.JWTService.decode_token",
        return_value={"exp": future_time},
    )

    with pytest.raises(services_exceptions.NotFoundTokenError) as exc_info:
        await AuthService.get_current_user(mock_session, "token_without_user_id")
    assert str(exc_info.value) == "User ID not found"


@pytest.mark.asyncio
async def test_get_current_user_integration(db_session):
    # Create test user
    async with db_session as session:
        test_user = UserModel(
            email="integration_auth@example.com",
            name="Integration Auth User",
            password=get_password_hash("secure_password"),
        )
        session.add(test_user)
        await session.commit()
        await session.refresh(test_user)

    # Generate real token
    token = JWTService.create_access_token(test_user.id)

    # Test get_current_user
    result = await AuthService.get_current_user(db_session, token)

    assert isinstance(result, UserResponseDTO)
    assert result.id == test_user.id
    assert result.email == test_user.email
