from unittest.mock import AsyncMock, Mock

from pytest import fixture
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.inbound.restapi.dependencies import user_service_dependency
from app.adapters.inbound.restapi.main import app
from app.adapters.outbound.repositories.models import DBUser
from app.domain.ports.user_repository import UserRepositoryPort
from app.domain.services.user_service import UserService


@fixture
def user_repository_mock():
    return Mock(spec=UserRepositoryPort)


@fixture
def user_service_mock():
    return Mock(spec=UserService)


@fixture
def mock_session():
    return AsyncMock(spec=AsyncSession)


@fixture
def fast_api_app(user_service_mock: UserService):
    app.dependency_overrides[user_service_dependency] = lambda: user_service_mock
    yield app
    app.dependency_overrides.clear()


@fixture
def make_fake_db_user():
    def _make_fake_db_user(email="test@example.com"):
        return DBUser(id=1, email=email, hashed_password="pwd", is_active=True)

    return _make_fake_db_user
