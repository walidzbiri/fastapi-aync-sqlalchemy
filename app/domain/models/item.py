from pydantic import BaseModel, ConfigDict


class Item(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    description: str
    owner_id: int


class CreateItemCommand(BaseModel):
    owner_id: int
    title: str
    description: str
