from abc import ABC, abstractmethod

from app.domain.models.user import CreateUserCommand, User


class UserRepositoryPort(ABC):
    @abstractmethod
    async def get_user(self, user_id: int) -> User:
        pass

    @abstractmethod
    async def get_user_by_email(self, email: str) -> User:
        pass

    @abstractmethod
    async def get_users(self, skip: int = 0, limit: int = 100) -> list[User]:
        pass

    @abstractmethod
    async def create_user(self, command: CreateUserCommand) -> User:
        pass

    @abstractmethod
    async def delete_user(self, user_id: int) -> None:
        pass
