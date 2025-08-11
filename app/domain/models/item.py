from pydantic import BaseModel


class Item(BaseModel):
    id: int
    title: str
    description: str
