from logging import getLogger

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.outbound.repositories.models import DBUser
from app.domain.models.user import CreateUserCommand, User
from app.domain.ports.exceptions import EntityAlreadyExists, EntityNotFound
from app.domain.ports.user_repository import UserRepositoryPort

logger = getLogger(__name__)


class PostgreSqlUserRepository(UserRepositoryPort):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_user(self, user_id: int) -> User:
        db_user = await self._session.get(DBUser, user_id)
        if db_user is None:
            logger.warning(f"User with id: {user_id} not found")
            raise EntityNotFound("User not found")
        return User.model_validate(db_user)

    async def get_user_by_email(self, email: str) -> User:
        query = select(DBUser).where(DBUser.email == email)
        result = await self._session.execute(query)
        db_user = result.scalar_one_or_none()
        if db_user is None:
            logger.warning(f"User with email: {email} not found")
            raise EntityNotFound("User not found")
        return User.model_validate(db_user)

    async def get_users(self, skip: int = 0, limit: int = 100) -> list[User]:
        query = select(DBUser).offset(skip).limit(limit)
        result = await self._session.execute(query)
        db_users = result.scalars().all()
        return [User.model_validate(db_user) for db_user in db_users]

    async def create_user(self, command: CreateUserCommand) -> User:
        try:
            await self.get_user_by_email(email=command.email)
        except EntityNotFound:
            fake_hashed_password = command.password + "notreallyhashed"
            db_user = DBUser(email=command.email, hashed_password=fake_hashed_password)
            self._session.add(db_user)
            await self._session.commit()
            await self._session.refresh(db_user)
            return User.model_validate(db_user)
        logger.warning(f"User with email: {command.email} already registered")
        raise EntityAlreadyExists("Email already registered")

    async def delete_user(self, user_id: int) -> None:
        db_user = await self._session.get(DBUser, user_id)
        if not db_user:
            logger.warning(f"User with id: {user_id} not found")
            raise EntityNotFound("User not found")
        await self._session.delete(db_user)
        await self._session.commit()
