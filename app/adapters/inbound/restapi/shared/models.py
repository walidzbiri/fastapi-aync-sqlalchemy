from __future__ import annotations

from pydantic import BaseModel

from app.domain.models.item import Item as DomainItem
from app.domain.models.user import User as DomainUser


class User(BaseModel):
    id: int
    email: str
    items: list[Item]

    @classmethod
    def from_domain(cls, domain_user: DomainUser) -> User:
        return cls(
            id=domain_user.id,
            email=domain_user.email,
            items=[Item.from_domain(item) for item in domain_user.items],
        )


class Item(BaseModel):
    id: int
    title: str
    description: str
    owner_id: int

    @classmethod
    def from_domain(cls, domain_item: DomainItem) -> Item:
        return cls(
            id=domain_item.id,
            title=domain_item.title,
            description=domain_item.description,
            owner_id=domain_item.owner_id,
        )
