from http import HTTPStatus

from app.adapters.inbound.restapi.exceptions import APIError


class UserNotFound(APIError):
    error_code = "USER.0001"
    status_code = HTTPStatus.NOT_FOUND
    detail = "User with id:{user_id} was not found"

    def __init__(self, user_id: str):
        super().__init__(
            detail=self.detail.format(user_id=user_id),
            status_code=self.status_code,
            error_code=self.error_code,
        )


class UserAlreadyExists(APIError):
    error_code = "USER.0002"
    status_code = HTTPStatus.CONFLICT
    detail = "User with email:{email} was already registered"

    def __init__(self, email: str):
        super().__init__(
            detail=self.detail.format(email=email),
            status_code=self.status_code,
            error_code=self.error_code,
        )
