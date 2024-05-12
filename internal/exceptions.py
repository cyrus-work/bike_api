from jwt import ExpiredSignatureError


class UserExistsException(Exception):
    """사용자를 찾았을 때 발생하는 예외"""

    def __init__(self, message="User exists"):
        super().__init__(message)


class JWTDataExpiredException(ExpiredSignatureError):
    """JWT 토큰이 만료되었을 때 발생하는 예외"""

    def __init__(self, message="JWT data has expired"):
        super().__init__(message)
