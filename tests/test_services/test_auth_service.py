import time
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.dto.tokendto import RefreshTokenDTO, CreateRefreshTokenDTO
from src.dto import UserLoginDTO, TokenDTO, UserResponseDTO
from src.services.auth_service import AuthService, get_password_hash, verify_password
from src.services.jwt_service import JWTService
from src.models import UserModel
from src.repositories import UserRepo, TokenRepo
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
    mock_session = AsyncMock(spec=AsyncSession)

    # Setup __aenter__ and __aexit__ for the mock session
    mock_session.__aenter__.return_value = mock_session
    mock_session.__aexit__.return_value = None

    user_email = "test@example.com"
    user_password = "secure_password"
    user_name = "Test User"
    password_hash = get_password_hash(user_password)
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
    mocker.patch(
        "src.repositories.token_repo.TokenRepo.count_tokens_for_user",
        new=AsyncMock(return_value=0),
    )
    mocker.patch(
        "src.repositories.token_repo.TokenRepo.add_token",
        new=AsyncMock(return_value=None),
    )

    # Mocking JWTService methods
    mock_create_access_token = mocker.patch(
        "src.services.jwt_service.JWTService.create_access_token",
        return_value="mocked_access_token",
    )
    mock_create_refresh_token = mocker.patch(
        "src.services.jwt_service.JWTService.create_refresh_token",
        return_value="mocked_refresh_token",
    )
    mock_get_expire_time = mocker.patch(
        "src.services.jwt_service.JWTService.get_expire_time",
        return_value="2025-01-31T23:59:59",
    )
    mock_verify_password = mocker.patch(
        "src.services.auth_service.verify_password",
        return_value=True,  # Assume password is correct
    )

    user_dto = UserLoginDTO(email=user_email, password=user_password)

    result = await AuthService.login_user(mock_session, user_dto)

    # Ckeck result
    assert isinstance(result, TokenDTO)
    assert result.token_type == "bearer"
    assert result.access_token == "mocked_access_token"
    assert result.refresh_token == "mocked_refresh_token"

    # Check method calls
    UserRepo.get_password_hash.assert_called_once_with(
        session=mock_session, email=user_email
    )
    UserRepo.find_by_email.assert_called_once_with(
        session=mock_session, email=user_email
    )
    TokenRepo.count_tokens_for_user.assert_called_once_with(
        session=mock_session, user_id=user_id
    )
    TokenRepo.add_token.assert_called_once_with(
        session=mock_session,
        token=mocker.ANY,
    )
    mock_verify_password.assert_called_once_with(user_password, password_hash)
    mock_create_access_token.assert_called_once_with(user_id)
    mock_create_refresh_token.assert_called_once_with(user_id)
    mock_get_expire_time.assert_called_once_with("mocked_refresh_token")
    mock_verify_password.assert_called_once_with(user_password, password_hash)

    # Check session closing
    mock_session.__aenter__.assert_called_once()
    mock_session.__aexit__.assert_called_once_with(None, None, None)


@pytest.mark.asyncio
async def test_login_user_invalid_password(mocker):
    # Preperation of mocks
    mock_session = AsyncMock(spec=AsyncSession)

    # Setup __aenter__ and __aexit__ for the mock session
    mock_session.__aenter__.return_value = mock_session
    mock_session.__aexit__.return_value = None

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

    UserRepo.get_password_hash.assert_called_once_with(
        session=mock_session, email=user_email
    )

    UserRepo.find_by_email.assert_not_called()

    assert result is None

    # Check session closing
    mock_session.__aenter__.assert_called_once()
    mock_session.__aexit__.assert_called_once_with(None, None, None)


@pytest.mark.asyncio
async def test_login_user_user_not_found(mocker):
    # Preperation of mocks
    mock_session = AsyncMock(spec=AsyncSession)

    # Setup __aenter__ and __aexit__ for the mock session
    mock_session.__aenter__.return_value = mock_session
    mock_session.__aexit__.return_value = None

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

    UserRepo.get_password_hash.assert_called_once_with(
        session=mock_session, email=user_email
    )
    UserRepo.find_by_email.assert_not_called()

    assert result is None

    # Check session closing
    mock_session.__aenter__.assert_called_once()
    mock_session.__aexit__.assert_called_once_with(None, None, None)


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
    assert "refresh_token" in result.model_dump()

    decoded_payload = JWTService.decode_token(result.access_token)
    decoded_refresh_payload = JWTService.decode_token(result.refresh_token)
    assert decoded_payload["sub"] == str(test_user.id)
    assert decoded_refresh_payload["sub"] == str(test_user.id)


@pytest.mark.asyncio
async def test_get_current_user_success(mocker):
    # Preperation of mocks
    mock_session = AsyncMock(spec=AsyncSession)

    user_id = 1
    user_email = "test@example.com"
    user_name = "Test User"
    test_user = UserResponseDTO(id=user_id, email=user_email, name=user_name)
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

    JWTService.decode_token.assert_called_once_with("valid_token")
    UserRepo.find_by_id.assert_called_once_with(mock_session, user_id)

    assert isinstance(result, UserResponseDTO)
    assert result.id == user_id
    assert result.email == user_email
    assert result.name == user_name


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


@pytest.mark.asyncio
async def test_refresh_token_success(mocker):
    # Preperation of mocks
    mock_session = AsyncMock(spec=AsyncSession)

    # Setup __aenter__ and __aexit__ for the mock session
    mock_session.__aenter__.return_value = mock_session
    mock_session.__aexit__.return_value = None

    user_id = 1
    refresh_token = "valid_refresh_token"

    mock_check_token_exist = mocker.patch(
        "src.repositories.token_repo.TokenRepo.check_token_exist",
        new=AsyncMock(return_value=RefreshTokenDTO(token=refresh_token)),
    )
    mock_create_refresh_token = mocker.patch(
        "src.services.jwt_service.JWTService.create_refresh_token",
        return_value="mocked_refresh_token",
    )
    mock_get_expire_time = mocker.patch(
        "src.services.jwt_service.JWTService.get_expire_time",
        return_value="2025-01-31T23:59:59",
    )
    mock_create_access_token = mocker.patch(
        "src.services.jwt_service.JWTService.create_access_token",
        return_value="mocked_access_token",
    )
    mock_update_token = mocker.patch(
        "src.repositories.token_repo.TokenRepo.update_token",
        new=AsyncMock(return_value=RefreshTokenDTO(token="mocked_refresh_token",))
    )
    result = await AuthService.refresh_token(
        mock_session, refresh_token=refresh_token, user_id=user_id
    )

    assert isinstance(result, TokenDTO)
    assert result.token_type == "bearer"
    assert result.access_token == "mocked_access_token"
    assert result.refresh_token == "mocked_refresh_token"

    mock_check_token_exist.assert_called_once_with(session=mock_session, token=refresh_token)
    mock_create_refresh_token.assert_called_once_with(user_id)
    mock_get_expire_time.assert_called_once_with("mocked_refresh_token")
    mock_update_token.assert_called_once_with(
        session=mock_session,
        old_token=refresh_token,
        new_token=CreateRefreshTokenDTO(
            token="mocked_refresh_token",
            user_id=user_id,
            expires_at="2025-01-31T23:59:59",
        ),
    )
    mock_create_access_token.assert_called_once_with(user_id)

    # Check session closing
    mock_session.__aenter__.assert_called_once()
    mock_session.__aexit__.assert_called_once_with(None, None, None)


@pytest.mark.asyncio
async def test_refresh_token_invalid_token(mocker):
    # Preperation of mocks
    mock_session = AsyncMock(spec=AsyncSession)

    # Setup __aenter__ and __aexit__ for the mock session
    mock_session.__aenter__.return_value = mock_session
    mock_session.__aexit__.return_value = None

    user_id = 1
    refresh_token = "invalid_refresh_token"

    mock_check_token_exist = mocker.patch(
        "src.repositories.token_repo.TokenRepo.check_token_exist",
        new=AsyncMock(return_value=None),
    )
    mock_create_refresh_token = mocker.patch(
        "src.services.jwt_service.JWTService.create_refresh_token",
        return_value="mocked_refresh_token",
    )

    with pytest.raises(services_exceptions.NotFoundTokenError) as exc_info:
        await AuthService.refresh_token(
            session=mock_session,
            refresh_token=refresh_token,
            user_id=user_id,
            )
    assert str(exc_info.value) == "Token not found"

    mock_check_token_exist.assert_called_once_with(session=mock_session, token=refresh_token)
    mock_create_refresh_token.assert_not_called()

    # Check session closing
    mock_session.__aenter__.assert_called_once()
    mock_session.__aexit__.assert_called_once_with(
        mocker.ANY,
        mocker.ANY,
        mocker.ANY,
    )


@pytest.mark.asyncio
async def test_refresh_token_integration(db_session):
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
    login_tokens = await AuthService.login_user(db_session, user_dto)
    time.sleep(1) # Wait for 1 second to make sure the tokens are different
    refreshed_tokens = await AuthService.refresh_token(
        db_session, login_tokens.refresh_token, test_user.id
    )

    assert isinstance(refreshed_tokens, TokenDTO)
    assert refreshed_tokens.token_type == "bearer"
    assert "access_token" in refreshed_tokens.model_dump()
    assert "refresh_token" in refreshed_tokens.model_dump()

    decoded_payload = JWTService.decode_token(refreshed_tokens.access_token)
    decoded_refresh_payload = JWTService.decode_token(refreshed_tokens.refresh_token)
    assert decoded_payload["sub"] == str(test_user.id)
    assert decoded_refresh_payload["sub"] == str(test_user.id)

    assert refreshed_tokens.access_token != login_tokens.access_token
    assert refreshed_tokens.refresh_token != login_tokens.refresh_token
