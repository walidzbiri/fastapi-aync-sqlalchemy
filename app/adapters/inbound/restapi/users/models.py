from __future__ import annotations

from pydantic import BaseModel

from app.domain.models import user as domain_entities


class User(BaseModel):
    id: int
    email: str

    @classmethod
    def from_domain(cls, domain_user: domain_entities.User) -> User:
        return cls(id=domain_user.id, email=domain_user.email)


class CreateUserRequest(BaseModel):
    email: str
    password: str

    def to_domain(self) -> domain_entities.CreateUserCommand:
        return domain_entities.CreateUserCommand(
            email=self.email, password=self.password
        )
