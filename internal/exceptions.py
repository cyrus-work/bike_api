# exceptions.py
from jwt import ExpiredSignatureError

exception_handlers = {}


def register_exception(cls):
    exception_handlers[cls] = (cls.status_code, cls.error_code, cls.message)
    return cls


@register_exception
class UserExistsException(Exception):
    status_code = 410
    error_code = 105
    message = "User exists"


@register_exception
class UserNotExistsException(Exception):
    status_code = 410
    error_code = 106
    message = "User not exists"


@register_exception
class JWTDataExpiredException(ExpiredSignatureError):
    status_code = 410
    error_code = 103
    message = "JWT data has expired"


@register_exception
class EmailNotConfirmException(Exception):
    status_code = 410
    error_code = 107
    message = "User email not confirmed"


@register_exception
class CheckerNotExistException(Exception):
    status_code = 410
    error_code = 108
    message = "User checker not exists"


@register_exception
class CheckerNotMatchException(Exception):
    status_code = 410
    error_code = 109
    message = "User checker not match"


@register_exception
class EmailNotExistException(Exception):
    status_code = 410
    error_code = 110
    message = "User email not exists"


@register_exception
class JWTRefreshNotExistException(ExpiredSignatureError):
    status_code = 410
    error_code = 111
    message = "JWT refresh token not exists"


@register_exception
class EmailVerifiedException(Exception):
    status_code = 410
    error_code = 112
    message = "Email verified"


@register_exception
class UserPwNotMatchException(Exception):
    status_code = 410
    error_code = 113
    message = "User password not match"


@register_exception
class LastWorkoutIdNotMatchException(Exception):
    status_code = 410
    error_code = 114
    message = "Workout last id not match"


@register_exception
class LastWorkoutOwnerNotMatchException(Exception):
    status_code = 410
    error_code = 115
    message = "Workout last owner not match"


@register_exception
class BikeNotExistsException(Exception):
    status_code = 410
    error_code = 116
    message = "Bike not exists"


@register_exception
class LastWorkoutNotExistsException(Exception):
    status_code = 410
    error_code = 117
    message = "Last workout not exists"


@register_exception
class AgencyNotExistsException(Exception):
    status_code = 410
    error_code = 118
    message = "Agency not exists"


@register_exception
class BikeIdNotMatchException(Exception):
    status_code = 410
    error_code = 119
    message = "Bike id not match"


@register_exception
class CredentialException(Exception):
    status_code = 410
    error_code = 120
    message = "Could not validate credentials"


@register_exception
class JWTErrorsException(Exception):
    status_code = 410
    error_code = 121
    message = "JWT errors"


@register_exception
class AdminRequiredException(Exception):
    status_code = 410
    error_code = 122
    message = "Admin required"


@register_exception
class RewardWorkoutNotExistsException(Exception):
    status_code = 410
    error_code = 123
    message = "Reward workout not exists"


@register_exception
class LastWorkoutActiveNotExistException(Exception):
    status_code = 410
    error_code = 125
    message = "Last workout active not exists"
