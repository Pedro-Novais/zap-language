from unittest.mock import Mock

import pytest

from core.manager.builder import CommandResponseBuilder
from core.manager.factory.handlers.command_handler import CommandHandler
from core.manager.services.conversation_session_service import ConversationSessionService
from core.model.enum import ConversationSessionsState


DEFAULT_PHONE = "5511999999999"


class TestCommandHandler:

    @pytest.fixture
    def session_service_mock(self) -> ConversationSessionService:
        return Mock(spec=ConversationSessionService)

    @pytest.fixture
    def handler(
        self,
        user_service_mock,
        message_history_service_mock,
        session_service_mock,
    ) -> CommandHandler:
        return CommandHandler(
            user_service=user_service_mock,
            message_history_service=message_history_service_mock,
            session_service=session_service_mock,
        )

    @pytest.fixture
    def session_model(self):
        return Mock(id="session-1", status=ConversationSessionsState.INITIALIZED)

    def test_is_command_returns_true_for_set_and_slash(self, handler: CommandHandler) -> None:
        assert handler.is_command("!reset") is True
        assert handler.is_command("/help") is True

    def test_is_command_returns_false_for_regular_text(self, handler: CommandHandler) -> None:
        assert handler.is_command("hello") is False

    def test_reply_message_handles_reset_command(
        self,
        handler: CommandHandler,
        user_service_mock,
        message_history_service_mock,
        session_model,
    ) -> None:
        response = handler.reply_message(
            user=Mock(),
            phone=DEFAULT_PHONE,
            message="!reset",
            session=session_model,
        )

        assert response == CommandResponseBuilder.response_for_reset_command()
        user_service_mock.invalidate_user_cache.assert_called_once_with(phone=DEFAULT_PHONE)
        message_history_service_mock.clear_message_history_for_user.assert_called_once_with(phone=DEFAULT_PHONE)

    def test_reply_message_handles_help_command(self, handler: CommandHandler, session_model) -> None:
        response = handler.reply_message(
            user=Mock(),
            phone=DEFAULT_PHONE,
            message="/help",
            session=session_model,
        )

        assert response == CommandResponseBuilder.response_for_help_command()

    def test_reply_message_handles_end_command(
        self,
        handler: CommandHandler,
        session_service_mock,
        session_model,
    ) -> None:
        response = handler.reply_message(
            user=Mock(),
            phone=DEFAULT_PHONE,
            message="/end",
            session=session_model,
        )

        assert response == CommandResponseBuilder.response_for_end_session_command()
        session_service_mock.set_session_state.assert_called_once_with(
            phone=DEFAULT_PHONE,
            session_id=session_model.id,
            state=ConversationSessionsState.CANCELLED_BY_USER,
        )

    def test_reply_message_returns_error_message_for_unknown_command(self, handler: CommandHandler, session_model) -> None:
        response = handler.reply_message(
            user=Mock(),
            phone=DEFAULT_PHONE,
            message="/unknown",
            session=session_model,
        )

        assert response == CommandResponseBuilder.response_for_error_command()

    def test_extract_key_after_command(self, handler: CommandHandler) -> None:
        assert handler._extract_key_after_command("/scenario aeroporto") == "aeroporto"
        assert handler._extract_key_after_command("/scenario") is None
