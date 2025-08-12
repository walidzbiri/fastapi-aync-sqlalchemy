from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends

from app.adapters.inbound.restapi.dependencies import user_service_dependency
from app.adapters.inbound.restapi.exceptions import InternalServerError
from app.adapters.inbound.restapi.users.exceptions import (
    UserAlreadyExists,
    UserNotFound,
)
from app.adapters.inbound.restapi.users.models import CreateUserRequest, User
from app.domain.ports.exceptions import EntityAlreadyExists, EntityNotFound
from app.domain.services.user_service import UserService

user_router = APIRouter()


@user_router.post(
    "/users",
    responses={
        UserAlreadyExists.status_code: {"model": UserAlreadyExists.schema()},
        InternalServerError.status_code: {"model": InternalServerError.schema()},
    },
)
async def create_user(
    payload: CreateUserRequest,
    user_service: Annotated[UserService, Depends(user_service_dependency)],
) -> User:
    try:
        user = await user_service.create_user(command=payload.to_domain())
    except EntityAlreadyExists:
        raise UserAlreadyExists(email=payload.email)
    return User.from_domain(domain_user=user)


@user_router.get(
    "/users/{user_id}",
    responses={
        UserNotFound.status_code: {"model": UserNotFound.schema()},
        InternalServerError.status_code: {"model": InternalServerError.schema()},
    },
)
async def get_user_by_id(
    user_id: int, user_service: Annotated[UserService, Depends(user_service_dependency)]
) -> User:
    try:
        user = await user_service.get_user(user_id=user_id)
    except EntityNotFound:
        raise UserNotFound(user_id=user_id)
    return User.from_domain(domain_user=user)


@user_router.get(
    "/users",
    responses={
        InternalServerError.status_code: {"model": InternalServerError.schema()},
    },
)
async def get_users(
    user_service: Annotated[UserService, Depends(user_service_dependency)],
) -> list[User]:
    users = await user_service.get_users()
    return [User.from_domain(domain_user=user) for user in users]


@user_router.delete(
    "/users/{user_id}",
    responses={
        UserNotFound.status_code: {"model": UserNotFound.schema()},
        InternalServerError.status_code: {"model": InternalServerError.schema()},
    },
    status_code=HTTPStatus.NO_CONTENT,
)
async def delete_user(
    user_id: int, user_service: Annotated[UserService, Depends(user_service_dependency)]
) -> None:
    try:
        await user_service.delete_user(user_id=user_id)
    except EntityNotFound:
        raise UserNotFound(user_id=user_id)
