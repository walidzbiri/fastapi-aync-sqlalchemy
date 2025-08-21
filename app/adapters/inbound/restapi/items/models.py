from pydantic import BaseModel

from app.domain.models import item as domain_entities


class CreateItemRequest(BaseModel):
    title: str
    description: str

    def to_domain(self, owner_id: int) -> domain_entities.CreateItemCommand:
        return domain_entities.CreateItemCommand(
            title=self.title, description=self.description, owner_id=owner_id
        )
