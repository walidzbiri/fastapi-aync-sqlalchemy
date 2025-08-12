from http import HTTPStatus

from pydantic import BaseModel, Field, create_model


class APIErrorSchema(BaseModel):
    error_code: str = Field(examples=["API.0000"])
    detail: str = Field(examples=["Internal Server Error"])


class APIError(Exception):
    status_code: int
    error_code: str
    detail: str

    def __init__(self, detail: str, status_code: int, error_code: str):
        self.detail = detail
        self.status_code = status_code
        self.error_code = error_code

    @classmethod
    def schema(cls) -> type[BaseModel]:
        return create_model(
            "APIErrorSchema", error_code=(str, cls.error_code), detail=(str, cls.detail)
        )


class InternalServerError(APIError):
    error_code = "API.0000"
    status_code = HTTPStatus.INTERNAL_SERVER_ERROR
    detail = "Internal server error, please try later or contact support team"

    def __init__(self) -> None:
        super().__init__(
            detail=self.detail, status_code=self.status_code, error_code=self.error_code
        )
