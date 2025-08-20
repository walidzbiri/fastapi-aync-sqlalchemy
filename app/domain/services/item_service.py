from app.domain.models.item import CreateItemCommand, Item
from app.domain.ports.item_repository import ItemRepositoryPort


class ItemService:
    def __init__(self, item_repository: ItemRepositoryPort):
        self._item_repository = item_repository

    async def create_user_item(self, command: CreateItemCommand) -> Item:
        return await self._item_repository.create_user_item(command)

    async def get_user_items(self, user_id: int) -> Item:
        return await self._item_repository.get_user_items(user_id)

    async def get_all_items(self) -> Item:
        return await self._item_repository.get_items()
