from logging import getLogger

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.outbound.repositories.models import DBItem, DBUser
from app.domain.models.item import CreateItemCommand, Item
from app.domain.ports.exceptions import EntityNotFound
from app.domain.ports.item_repository import ItemRepositoryPort

logger = getLogger(__name__)


class PostgreSqlItemRepository(ItemRepositoryPort):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def create_user_item(self, command: CreateItemCommand) -> Item:
        db_user = await self._session.get(DBUser, command.owner_id)
        if db_user is None:
            logger.warning(f"User with id: {command.owner_id} not found")
            raise EntityNotFound(f"User {command.owner_id} not found")
        db_item = DBItem(
            title=command.title,
            description=command.description,
            owner_id=command.owner_id,
        )
        self._session.add(db_item)
        await self._session.commit()
        await self._session.refresh(db_item)
        return Item.model_validate(db_item)

    async def get_user_items(self, user_id: int) -> list[Item]:
        db_user = await self._session.get(DBUser, user_id)
        if db_user is None:
            logger.warning(f"User with id: {user_id} not found")
            raise EntityNotFound(f"User {user_id} not found")
        return [
            Item.model_validate(db_item)
            for db_item in await db_user.awaitable_attrs.items
        ]

    async def get_items(self) -> list[Item]:
        query = select(DBItem)
        result = await self._session.execute(query)
        db_items = result.scalars().all()
        return [Item.model_validate(db_item) for db_item in db_items]
