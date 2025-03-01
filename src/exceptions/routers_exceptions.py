from fastapi import HTTPException, status


class BaseAPIException(HTTPException):
    status_code = 500  # <-- Default value
    detail = ""

    def __init__(self):
        super().__init__(status_code=self.status_code, detail=self.detail)


class UserAlreadyExistError(BaseAPIException):
    status_code = status.HTTP_409_CONFLICT
    detail = "User with this email already exists"


class UnauthorizedError(BaseAPIException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Unauthorized"


class WrongLoginDataError(UnauthorizedError):
    detail = "Incorrect email or password"


class InvalidAuthHeaderFormat(UnauthorizedError):
    detail = "Invalid Authorization header format"


class InvalidToken(UnauthorizedError):
    detail = "Token is not valid"


class ExpiredToken(InvalidToken):
    detail = "Token is expired"


class NotFoundUser(UnauthorizedError):
    detail = "User not found"


class NotFoundToDo(BaseAPIException):
    status_code = status.HTTP_404_NOT_FOUND
    detail = "Todo with this ID not found"


class ForbiddenError(BaseAPIException):
    status_code = status.HTTP_403_FORBIDDEN
    detail = "Forbidden"
