from typing import Annotated

from fastapi import APIRouter, Depends

from app.adapters.inbound.restapi.dependencies import item_service_dependency
from app.adapters.inbound.restapi.exceptions import InternalServerError
from app.adapters.inbound.restapi.items.models import CreateItemRequest
from app.adapters.inbound.restapi.shared.models import Item
from app.adapters.inbound.restapi.users.exceptions import UserNotFound
from app.domain.ports.exceptions import EntityNotFound
from app.domain.services.item_service import ItemService

item_router = APIRouter(tags=["items"])


@item_router.post(
    "/users/{user_id}/items",
    responses={
        UserNotFound.status_code: {"model": UserNotFound.schema()},
        InternalServerError.status_code: {"model": InternalServerError.schema()},
    },
)
async def create_user_item(
    user_id: int,
    payload: CreateItemRequest,
    item_service: Annotated[ItemService, Depends(item_service_dependency)],
) -> Item:
    try:
        item = await item_service.create_user_item(
            command=payload.to_domain(owner_id=user_id)
        )
    except EntityNotFound:
        raise UserNotFound(user_id)
    return Item.from_domain(domain_item=item)


@item_router.get(
    "/users/{user_id}/items",
    responses={
        UserNotFound.status_code: {"model": UserNotFound.schema()},
        InternalServerError.status_code: {"model": InternalServerError.schema()},
    },
)
async def get_user_items(
    user_id: int,
    item_service: Annotated[ItemService, Depends(item_service_dependency)],
) -> list[Item]:
    try:
        items = await item_service.get_user_items(user_id)
    except EntityNotFound:
        raise UserNotFound(user_id)
    return [Item.from_domain(domain_item=item) for item in items]


@item_router.get(
    "/items",
    responses={
        InternalServerError.status_code: {"model": InternalServerError.schema()},
    },
)
async def get_all_items(
    item_service: Annotated[ItemService, Depends(item_service_dependency)],
) -> list[Item]:
    items = await item_service.get_all_items()
    return [Item.from_domain(domain_item=item) for item in items]
