from unittest.mock import AsyncMock

import pytest

from app.adapters.outbound.repositories.models import DBUser
from app.adapters.outbound.repositories.user_repository import PostgreSqlUserRepository
from app.domain.models.user import CreateUserCommand, User
from app.domain.ports.exceptions import EntityAlreadyExists, EntityNotFound


@pytest.mark.asyncio
class TestPostgreSqlUserRepository:
    async def test_get_user_found(self, make_fake_db_user):
        mock_session = AsyncMock()
        fake_db_user = make_fake_db_user()
        mock_session.get.return_value = fake_db_user

        repo = PostgreSqlUserRepository(mock_session)
        result = await repo.get_user(1)

        mock_session.get.assert_called_once_with(DBUser, 1)
        assert isinstance(result, User)
        assert result.email == fake_db_user.email

    async def test_get_user_not_found(self):
        mock_session = AsyncMock()
        mock_session.get.return_value = None

        repo = PostgreSqlUserRepository(mock_session)
        with pytest.raises(EntityNotFound):
            await repo.get_user(42)

    async def test_create_user_success(self, make_fake_db_user):
        mock_session = AsyncMock()

        repo = PostgreSqlUserRepository(mock_session)
        repo.get_user_by_email = AsyncMock(side_effect=EntityNotFound)

        fake_db_user = make_fake_db_user(email="new@example.com")
        mock_session.refresh = AsyncMock()
        mock_session.refresh.side_effect = lambda obj: obj.__dict__.update(
            fake_db_user.__dict__
        )

        cmd = CreateUserCommand(email="new@example.com", password="1234")
        result = await repo.create_user(cmd)

        assert isinstance(result, User)
        assert result.email == "new@example.com"
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()

    async def test_create_user_already_exists(self):
        mock_session = AsyncMock()

        repo = PostgreSqlUserRepository(mock_session)
        repo.get_user_by_email = AsyncMock(
            return_value=User(
                id=1, email="test@example.com", hashed_password="pwd", is_active=True
            )
        )

        cmd = CreateUserCommand(email="test@example.com", password="1234")

        with pytest.raises(EntityAlreadyExists):
            await repo.create_user(cmd)
