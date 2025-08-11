from abc import ABC, abstractmethod

from app.domain.models.item import Item


class ItemRepositoryPort(ABC):
    @abstractmethod
    async def get_items(self) -> list[Item]:
        pass

    @abstractmethod
    async def create_user_item(self, item: Item) -> Item:
        pass
