from abc import ABC, abstractmethod

from app.domain.models.item import CreateItemCommand, Item


class ItemRepositoryPort(ABC):
    @abstractmethod
    async def create_user_item(self, command: CreateItemCommand) -> Item:
        pass

    @abstractmethod
    async def get_user_items(self, user_id: int) -> list[Item]:
        pass

    @abstractmethod
    async def get_items(self) -> list[Item]:
        pass
