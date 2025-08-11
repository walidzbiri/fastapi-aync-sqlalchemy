from pydantic import BaseModel, ConfigDict

from app.domain.models.item import Item


class User(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    email: str
    is_active: bool

    items: list[Item] = []


class CreateUserCommand(BaseModel):
    email: str
    password: str
