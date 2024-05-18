from jwt import ExpiredSignatureError


class UserExistsException(Exception):
    """사용자를 찾았을 때 발생하는 예외"""

    def __init__(self, message="User exists"):
        super().__init__(message)


class UserNotExistsException(Exception):
    """사용자를 찾지 못했을 때 발생하는 예외"""

    def __init__(self, message="User not exists"):
        super().__init__(message)


class JWTDataExpiredException(ExpiredSignatureError):
    """JWT 토큰이 만료되었을 때 발생하는 예외"""

    def __init__(self, message="JWT data has expired"):
        super().__init__(message)


class UserEmailNotConfirmException(Exception):
    """사용자 이메일 확인 예외"""

    def __init__(self, message="User email not confirmed"):
        super().__init__(message)


class UserCheckerNotExistException(Exception):
    """사용자 체크가 없을 때 발생하는 예외"""

    def __init__(self, message="User checker not exists"):
        super().__init__(message)


class UserCheckerNotMatchException(Exception):
    """사용자 체크가 일치하지 않을 때 발생하는 예외"""

    def __init__(self, message="User checker not match"):
        super().__init__(message)


class UserEmailNotExistException(Exception):
    """사용자 이메일이 없을 때 발생하는 예외"""

    def __init__(self, message="User email not exists"):
        super().__init__(message)


class JWTRefreshTokenNotExistException(ExpiredSignatureError):
    """JWT 리프레시 토큰이 만료되었을 때 발생하는 예외"""

    def __init__(self, message="JWT refresh token not exists"):
        super().__init__(message)


class EmailVerifiedException(Exception):
    """이메일이 확인되었을 때 발생하는 예외"""

    def __init__(self, message="Email verified"):
        super().__init__(message)


class UserPasswordNotMatchException(Exception):
    """사용자 비밀번호가 일치하지 않을 때 발생하는 예외"""

    def __init__(self, message="User password not match"):
        super().__init__(message)


class LastWorkoutIdNotMatchException(Exception):
    """Workout 마지막 ID가 일치하지 않을 때 발생하는 예외"""

    def __init__(self, message="Workout last id not match"):
        super().__init__(message)


class WorkoutLastOwnerNotMatchException(Exception):
    """Workout 마지막 소유자가 일치하지 않을 때 발생하는 예외"""

    def __init__(self, message="Workout last owner not match"):
        super().__init__(message)


class BikeNotExistsException(Exception):
    """Bike가 없을 때 발생하는 예외"""

    def __init__(self, message="Bike not exists"):
        super().__init__(message)


class LastWorkoutNotExistsException(Exception):
    """마지막 workout이 없을 때 발생하는 예외"""

    def __init__(self, message="Last workout not exists"):
        super().__init__(message)


class AgencyNotExistsException(Exception):
    """Agency가 없을 때 발생하는 예외"""

    def __init__(self, message="Agency not exists"):
        super().__init__(message)


class BikeIdNotMatchException(Exception):
    """Bike ID가 일치하지 않을 때 발생하는 예외"""

    def __init__(self, message="Bike id not match"):
        super().__init__(message)
