from jose import JWTError


class NotValidTokenError(JWTError):
    pass


class ExpiredSignatureTokenError(JWTError):
    pass


class NotFoundTokenError(JWTError):
    pass
