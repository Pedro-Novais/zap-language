from datetime import datetime
from unittest.mock import Mock, patch

import pytest
from faker import Faker

from external.repositories.supabase.user_repository_impl import UserRepositoryImpl
from core.model import UserModel

fake = Faker()


class TestUserRepositoryImpl:

    @pytest.fixture
    def repository(self):
        return UserRepositoryImpl()

    def test_get_user_by_sub_success(self, repository: UserRepositoryImpl):
        # Arrange
        sub = "google-sub-123"
        mock_user = Mock()
        mock_user.id = fake.uuid4()
        mock_user.email = "user@example.com"
        mock_user.name = "User Name"
        mock_user.phone = None
        mock_user.whatsapp_enabled = False
        mock_user.is_valid = True
        mock_user.is_admin = False
        mock_user.created_at = datetime.now()
        mock_user.google_id = None
        mock_user.sub = sub
        mock_user.last_login = datetime.now()
        mock_user.password = "hashed-password"
        mock_user.study_settings = None

        expected_model = UserModel(
            id=mock_user.id,
            email=mock_user.email,
            name=mock_user.name,
            phone=mock_user.phone,
            whatsapp_enabled=mock_user.whatsapp_enabled,
            is_valid=mock_user.is_valid,
            is_admin=mock_user.is_admin,
            created_at=mock_user.created_at,
            google_id=mock_user.google_id,
            sub=mock_user.sub,
            last_login=mock_user.last_login,
            study_settings=None,
            password=mock_user.password,
        )

        with patch('external.repositories.supabase.user_repository_impl.get_db_session') as mock_session:
            mock_session.return_value.__enter__.return_value.query.return_value.filter.return_value.first.return_value = mock_user

            # Act
            result = repository.get_user_by_sub(sub)

            # Assert
            assert result == expected_model

    def test_get_user_by_sub_not_found(self, repository: UserRepositoryImpl):
        # Arrange
        sub = "non-existent-sub"

        with patch('external.repositories.supabase.user_repository_impl.get_db_session') as mock_session:
            mock_session.return_value.__enter__.return_value.query.return_value.filter.return_value.first.return_value = None

            # Act
            result = repository.get_user_by_sub(sub)

            # Assert
            assert result is None

    def test_create_google_user(self, repository: UserRepositoryImpl):
        # Arrange
        name = "New User"
        email = "new@example.com"
        sub = "google-sub-456"
        password_hash = "hashed-password"
        last_login = datetime.now()

        mock_user = Mock()
        mock_user.id = fake.uuid4()
        mock_user.email = email
        mock_user.name = name
        mock_user.sub = sub
        mock_user.password = password_hash
        mock_user.last_login = last_login
        mock_user.is_valid = True
        mock_user.phone = None
        mock_user.whatsapp_enabled = False
        mock_user.is_admin = False
        mock_user.created_at = datetime.now()
        mock_user.google_id = None
        mock_user.study_settings = None

        with patch('external.repositories.supabase.user_repository_impl.get_db_session') as mock_session:
            mock_session_instance = mock_session.return_value.__enter__.return_value
            mock_session_instance.add.return_value = None
            mock_session_instance.commit.return_value = None
            mock_session_instance.refresh.return_value = None

            # Mock the query for _transform_user_data_in_user_model
            mock_session_instance.query.return_value.filter.return_value.first.return_value = mock_user

            # Act
            result = repository.create_google_user(name, email, sub, password_hash, last_login)

            # Assert
            assert result.name == name
            assert result.email == email
            assert result.sub == sub
            mock_session_instance.add.assert_called_once()
            mock_session_instance.commit.assert_called_once()

    def test_update_google_login(self, repository: UserRepositoryImpl):
        # Arrange
        user_id = str(fake.uuid4())
        sub = "updated-sub"
        last_login = datetime.now()

        mock_user = Mock()
        mock_user.id = user_id
        mock_user.sub = sub
        mock_user.last_login = last_login

        with patch('external.repositories.supabase.user_repository_impl.get_db_session') as mock_session:
            mock_session_instance = mock_session.return_value.__enter__.return_value
            mock_session_instance.query.return_value.filter.return_value.first.return_value = mock_user
            mock_session_instance.commit.return_value = None
            mock_session_instance.refresh.return_value = None

            # Act
            result = repository.update_google_login(user_id, sub, last_login)

            # Assert
            assert result.sub == sub
            assert result.last_login == last_login
            mock_session_instance.commit.assert_called_once()