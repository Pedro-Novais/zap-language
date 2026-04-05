from unittest.mock import Mock

import pytest

from core.manager.factory.handlers.undefined_handler import UndefinedHandler
from core.manager.services.conversation_session_service import ConversationSessionService
from core.model.enum import ConversationSessionsState
from core.shared.model.answers import UndefinedAnswers


DEFAULT_PHONE = "5511999999999"


class TestUndefinedHandler:

    @pytest.fixture
    def session_service_mock(self) -> ConversationSessionService:
        return Mock(spec=ConversationSessionService)

    @pytest.fixture
    def handler(
        self,
        whatsapp_service_mock,
        redis_service_mock,
        user_service_mock,
        session_service_mock,
    ) -> UndefinedHandler:
        return UndefinedHandler(
            whatsapp_service=whatsapp_service_mock,
            redis_service=redis_service_mock,
            user_service=user_service_mock,
            session_service=session_service_mock,
        )

    @pytest.fixture
    def user_model(self):
        return Mock(id="user-1")

    def test_reply_message_initialized_updates_state_and_returns_welcome(
        self,
        handler: UndefinedHandler,
        session_service_mock,
        user_model,
    ) -> None:
        session = Mock(id="session-1", status=ConversationSessionsState.INITIALIZED)

        response = handler.reply_message(
            user=user_model,
            phone=DEFAULT_PHONE,
            message="oi",
            session=session,
        )

        assert response == UndefinedAnswers.SESSION_STARTED
        session_service_mock.set_session_state.assert_called_once_with(
            phone=DEFAULT_PHONE,
            session_id="session-1",
            state=ConversationSessionsState.AWAITING_DEFINITION,
        )

    def test_reply_message_awaiting_definition_returns_welcome(
        self,
        handler: UndefinedHandler,
        session_service_mock,
        user_model,
    ) -> None:
        session = Mock(id="session-1", status=ConversationSessionsState.AWAITING_DEFINITION)

        response = handler.reply_message(
            user=user_model,
            phone=DEFAULT_PHONE,
            message="oi",
            session=session,
        )

        assert response == UndefinedAnswers.SESSION_STARTED
        session_service_mock.set_session_state.assert_not_called()

    def test_reply_message_invalid_state_raises_not_implemented(
        self,
        handler: UndefinedHandler,
        user_model,
    ) -> None:
        session = Mock(id="session-1", status=ConversationSessionsState.ERROR)

        with pytest.raises(NotImplementedError):
            handler.reply_message(
                user=user_model,
                phone=DEFAULT_PHONE,
                message="oi",
                session=session,
            )
