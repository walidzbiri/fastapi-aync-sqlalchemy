import pytest

from app.domain.models.user import CreateUserCommand, User
from app.domain.ports.exceptions import EntityAlreadyExists, EntityNotFound
from app.domain.services.user_service import UserService


@pytest.mark.asyncio
class TestUserService:
    async def test_get_user__happy_path(self, user_repository_mock):
        # Given
        expected_user = User(
            id=1,
            email="john.doe@gmail.com",
            is_active=True,
        )
        user_repository_mock.get_user.return_value = expected_user
        user_service = UserService(user_repository=user_repository_mock)
        # When
        result = await user_service.get_user(user_id=1)
        # Then
        assert result == expected_user
        user_repository_mock.get_user.assert_called_once_with(1)

    async def test_get_user__not_found(self, user_repository_mock):
        # Given
        user_repository_mock.get_user.side_effect = EntityNotFound
        user_service = UserService(user_repository=user_repository_mock)
        # When Then
        with pytest.raises(EntityNotFound):
            await user_service.get_user(user_id=1)
        user_repository_mock.get_user.assert_called_once_with(1)

    async def test_get_user_by_email__happy_path(self, user_repository_mock):
        # Given
        expected_user = User(
            id=1,
            email="john.doe@gmail.com",
            is_active=True,
        )
        user_repository_mock.get_user_by_email.return_value = expected_user
        user_service = UserService(user_repository=user_repository_mock)
        # When
        result = await user_service.get_user_by_email(email=expected_user.email)
        # Then
        assert result == expected_user
        user_repository_mock.get_user_by_email.assert_called_once_with(
            expected_user.email
        )

    async def test_get_user_by_email__not_found(self, user_repository_mock):
        # Given
        user_repository_mock.get_user_by_email.side_effect = EntityNotFound
        user_service = UserService(user_repository=user_repository_mock)
        # When Then
        with pytest.raises(EntityNotFound):
            await user_service.get_user_by_email(email="bob@email.com")
        user_repository_mock.get_user_by_email.assert_called_once_with("bob@email.com")

    async def test_get_users__happy_path(self, user_repository_mock):
        # Given
        expected_users = [
            User(
                id=1,
                email="john.doe@gmail.com",
                is_active=True,
            ),
            User(
                id=2,
                email="sofie.doe@gmail.com",
                is_active=False,
            ),
        ]
        user_repository_mock.get_users.return_value = expected_users
        user_service = UserService(user_repository=user_repository_mock)
        # When
        result = await user_service.get_users()
        # Then
        assert result == expected_users
        user_repository_mock.get_users.assert_called_once_with(skip=0, limit=100)

    async def test_create_user__happy_path(self, user_repository_mock):
        # Given
        expected_user = User(
            id=1,
            email="john.doe@gmail.com",
            is_active=True,
        )
        create_user_command = CreateUserCommand(
            email=expected_user.email, password="bobi"
        )
        user_repository_mock.create_user.return_value = expected_user
        user_service = UserService(user_repository=user_repository_mock)
        # When
        result = await user_service.create_user(command=create_user_command)
        # Then
        assert result == expected_user
        user_repository_mock.create_user.assert_called_once_with(create_user_command)

    async def test_create_user__user_already_exists(self, user_repository_mock):
        # Given
        expected_user = User(
            id=1,
            email="john.doe@gmail.com",
            is_active=True,
        )
        create_user_command = CreateUserCommand(
            email=expected_user.email, password="bobi"
        )

        user_repository_mock.create_user.side_effect = EntityAlreadyExists
        user_service = UserService(user_repository=user_repository_mock)
        # When Then
        with pytest.raises(EntityAlreadyExists):
            await user_service.create_user(command=create_user_command)
        user_repository_mock.create_user.assert_called_once_with(create_user_command)

    async def test_delete_user__happy_path(self, user_repository_mock):
        # Given
        expected_user = User(
            id=1,
            email="john.doe@gmail.com",
            is_active=True,
        )
        user_repository_mock.delete_user.return_value = None
        user_service = UserService(user_repository=user_repository_mock)
        # When
        result = await user_service.delete_user(user_id=expected_user.id)
        # Then
        assert result is None
        user_repository_mock.delete_user.assert_called_once_with(expected_user.id)

    async def test_delete_user__not_found(self, user_repository_mock):
        # Given
        expected_user = User(
            id=1,
            email="john.doe@gmail.com",
            is_active=True,
        )
        user_repository_mock.delete_user.side_effect = EntityNotFound
        user_service = UserService(user_repository=user_repository_mock)
        # When Then
        with pytest.raises(EntityNotFound):
            await user_service.delete_user(user_id=expected_user.id)
        user_repository_mock.delete_user.assert_called_once_with(expected_user.id)
