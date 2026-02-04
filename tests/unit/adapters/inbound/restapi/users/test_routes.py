from http import HTTPStatus
from unittest.mock import ANY

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from app.domain.models.user import User
from app.domain.ports.exceptions import EntityAlreadyExists, EntityNotFound
from app.domain.services.user_service import UserService


@pytest.mark.asyncio
class TestUserRoutes:
    async def test_create_user__happy_path(
        self, fast_api_app: FastAPI, user_service_mock: UserService
    ):
        # GIVEN
        user_service_mock.create_user.return_value = User(
            id=1,
            email="john.doe@email.com",
            is_active=True,
        )
        # WHEN
        async with AsyncClient(
            transport=ASGITransport(app=fast_api_app, raise_app_exceptions=False),
            base_url="http://test",
        ) as client:
            response = await client.post(
                "/users", json={"email": "john.doe@email.com", "password": "bob"}
            )

        # THEN
        assert response.status_code == HTTPStatus.OK
        assert response.json() == {
            "id": ANY,
            "email": "john.doe@email.com",
            "items": [],
        }

    async def test_create_user__already_exists(
        self, fast_api_app: FastAPI, user_service_mock: UserService
    ):
        # GIVEN
        user_service_mock.create_user.side_effect = EntityAlreadyExists
        # WHEN
        async with AsyncClient(
            transport=ASGITransport(app=fast_api_app, raise_app_exceptions=False),
            base_url="http://test",
        ) as client:
            response = await client.post(
                "/users", json={"email": "john.doe@email.com", "password": "bob"}
            )

        # THEN
        assert response.status_code == HTTPStatus.CONFLICT
        assert response.json() == {
            "error": "USER.0002",
            "detail": "User with email:john.doe@email.com was already registered",
        }

    async def test_get_user_by_id__happy_path(
        self, fast_api_app: FastAPI, user_service_mock: UserService
    ):
        # GIVEN
        user_service_mock.get_user.return_value = User(
            id=1,
            email="john.doe@email.com",
            is_active=True,
        )
        # WHEN
        async with AsyncClient(
            transport=ASGITransport(app=fast_api_app, raise_app_exceptions=False),
            base_url="http://test",
        ) as client:
            response = await client.get("/users/1")

        # THEN
        assert response.status_code == HTTPStatus.OK
        assert response.json() == {"id": 1, "email": "john.doe@email.com", "items": []}

    async def test_get_user_by_id__not_found(
        self, fast_api_app: FastAPI, user_service_mock: UserService
    ):
        # GIVEN
        user_service_mock.get_user.side_effect = EntityNotFound
        # WHEN
        async with AsyncClient(
            transport=ASGITransport(app=fast_api_app, raise_app_exceptions=False),
            base_url="http://test",
        ) as client:
            response = await client.get("/users/1")

        # THEN
        assert response.status_code == HTTPStatus.NOT_FOUND
        assert response.json() == {
            "error": "USER.0001",
            "detail": "User with id:1 was not found",
        }

    async def test_get_users__happy_path(
        self, fast_api_app: FastAPI, user_service_mock: UserService
    ):
        # GIVEN
        user_service_mock.get_users.return_value = [
            User(
                id=1,
                email="john.doe@email.com",
                is_active=True,
            ),
            User(
                id=2,
                email="sofie.doe@email.com",
                is_active=True,
            ),
        ]
        # WHEN
        async with AsyncClient(
            transport=ASGITransport(app=fast_api_app, raise_app_exceptions=False),
            base_url="http://test",
        ) as client:
            response = await client.get("/users")

        # THEN
        assert response.status_code == HTTPStatus.OK
        assert response.json() == [
            {"id": 1, "email": "john.doe@email.com", "items": []},
            {"id": 2, "email": "sofie.doe@email.com", "items": []},
        ]

    async def test_deleted_user_by_id__happy_path(
        self, fast_api_app: FastAPI, user_service_mock: UserService
    ):
        # GIVEN
        user_service_mock.delete_user.return_value = None
        # WHEN
        async with AsyncClient(
            transport=ASGITransport(app=fast_api_app, raise_app_exceptions=False),
            base_url="http://test",
        ) as client:
            response = await client.delete("/users/1")

        # THEN
        assert response.status_code == HTTPStatus.NO_CONTENT
        assert response.text == ""

    async def test_delete_user_by_id__not_found(
        self, fast_api_app: FastAPI, user_service_mock: UserService
    ):
        # GIVEN
        user_service_mock.delete_user.side_effect = EntityNotFound
        # WHEN
        async with AsyncClient(
            transport=ASGITransport(app=fast_api_app, raise_app_exceptions=False),
            base_url="http://test",
        ) as client:
            response = await client.delete("/users/1")

        # THEN
        assert response.status_code == HTTPStatus.NOT_FOUND
        assert response.json() == {
            "error": "USER.0001",
            "detail": "User with id:1 was not found",
        }
