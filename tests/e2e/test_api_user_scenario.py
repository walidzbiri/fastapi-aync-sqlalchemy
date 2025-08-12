from http import HTTPStatus

import pytest
import pytest_asyncio
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from app.adapters.inbound.restapi.dependencies import async_engine_dependency
from app.adapters.inbound.restapi.main import app


@pytest_asyncio.fixture(scope="function")
async def sqlalchemy_engine_dependency() -> AsyncEngine:
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", future=True)
    from app.adapters.outbound.repositories.models import Base

    async with engine.connect() as connection:
        await connection.run_sync(Base.metadata.create_all)
        await connection.commit()

    yield engine

    async with engine.connect() as connection:
        await connection.run_sync(Base.metadata.drop_all)
        await connection.commit()


@pytest.fixture(scope="function")
def rest_api(sqlalchemy_engine_dependency: AsyncEngine) -> FastAPI:
    app.dependency_overrides[async_engine_dependency] = (
        lambda: sqlalchemy_engine_dependency
    )
    yield app
    app.dependency_overrides.clear()


@pytest.mark.asyncio
class TestUsersAPI:
    async def test__users__crud(self, rest_api: FastAPI):
        async with AsyncClient(
            transport=ASGITransport(app=rest_api, raise_app_exceptions=False),
            base_url="http://test",
        ) as client:
            empty_users_list_response = await client.get("/users")
            assert empty_users_list_response.status_code == HTTPStatus.OK
            assert empty_users_list_response.json() == []

            created_user_response = await client.post(
                "/users", json={"email": "bob@email.com", "password": "bob"}
            )
            assert created_user_response.status_code == HTTPStatus.OK
            assert created_user_response.json() == {"id": 1, "email": "bob@email.com"}

            created_user2_response = await client.post(
                "/users", json={"email": "bob@email.com", "password": "bob"}
            )
            assert created_user2_response.status_code == HTTPStatus.CONFLICT
            assert created_user2_response.json() == {
                "error": "USER.0002",
                "detail": "User with email:bob@email.com was already registred",
            }

            users_list_response = await client.get("/users")
            assert users_list_response.status_code == HTTPStatus.OK
            assert users_list_response.json() == [{"id": 1, "email": "bob@email.com"}]

            deleted_user = await client.delete("/users/1")
            assert deleted_user.status_code == HTTPStatus.NO_CONTENT
            assert deleted_user.text == ""

            deleted_user_again = await client.delete("/users/1")
            assert deleted_user_again.status_code == HTTPStatus.NOT_FOUND
            assert deleted_user_again.json() == {
                "error": "USER.0001",
                "detail": "User with id:1 was not found",
            }
