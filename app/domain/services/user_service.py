from app.domain.models.user import CreateUserCommand, User
from app.domain.ports.user_repository import UserRepositoryPort


class UserService:
    def __init__(self, user_repository: UserRepositoryPort):
        self.user_repository = user_repository

    async def get_user(self, user_id: int) -> User:
        return await self.user_repository.get_user(user_id)

    async def get_user_by_email(self, email: str) -> User:
        return await self.user_repository.get_user_by_email(email)

    async def get_users(self, skip: int = 0, limit: int = 100) -> list[User]:
        return await self.user_repository.get_users(skip=skip, limit=limit)

    async def create_user(self, command: CreateUserCommand) -> User:
        return await self.user_repository.create_user(command)

    async def delete_user(self, user_id: int) -> None:
        return await self.user_repository.delete_user(user_id)
