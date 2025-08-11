from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from app.adapters.outbound.repositories.user_repository import PostgreSqlUserRepository
from app.domain.ports.user_repository import UserRepositoryPort
from app.domain.services.user_service import UserService

SQLALCHEMY_DATABASE_URL = "postgresql+asyncpg://postgres:changeme@postgres/postgres"
engine = create_async_engine(SQLALCHEMY_DATABASE_URL)


async def sqlalchemy_session_dependency() -> AsyncGenerator[AsyncSession, None]:
    session = AsyncSession(engine, expire_on_commit=True)
    try:
        yield session
    finally:
        await session.close()


def user_repository_dependency(
    sqlalchemy_session: Annotated[AsyncSession, Depends(sqlalchemy_session_dependency)],
) -> UserRepositoryPort:
    return PostgreSqlUserRepository(session=sqlalchemy_session)


def user_service_dependency(
    user_repository: Annotated[UserRepositoryPort, Depends(user_repository_dependency)],
):
    return UserService(user_repository=user_repository)
