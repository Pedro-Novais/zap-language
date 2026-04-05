from unittest.mock import Mock

import pytest

from core.manager.factory.handlers.free_talk_handler import FreeTalkHandler
from core.manager.services.conversation_session_service import ConversationSessionService
from core.model.enum import ConversationSessionsState
from core.shared.errors import GlobalIALockError, SessionActiveError, SessionStateInvalidError


DEFAULT_PHONE = "5511999999999"


class TestFreeTalkHandler:

    @pytest.fixture
    def session_service_mock(self) -> ConversationSessionService:
        return Mock(spec=ConversationSessionService)

    @pytest.fixture
    def handler(
        self,
        ai_tutor_service_mock,
        redis_service_mock,
        user_service_mock,
        message_history_service_mock,
        session_service_mock,
    ) -> FreeTalkHandler:
        handler = FreeTalkHandler(
            ai_tutor_service=ai_tutor_service_mock,
            redis_service=redis_service_mock,
            user_service=user_service_mock,
            message_history_service=message_history_service_mock,
            session_service=session_service_mock,
        )
        handler.instruction_builder.build_free_talk_instruction = Mock(return_value="instruction")
        return handler

    @pytest.fixture
    def user_model(self):
        return Mock(id="user-1")

    @pytest.fixture
    def initialized_session(self):
        return Mock(id="session-1", status=ConversationSessionsState.INITIALIZED)

    @pytest.fixture
    def practicing_session(self):
        return Mock(id="session-2", status=ConversationSessionsState.PRACTICING)

    @pytest.fixture
    def invalid_session(self):
        return Mock(id="session-3", status=ConversationSessionsState.ERROR)

    def test_is_command(self, handler: FreeTalkHandler) -> None:
        assert handler.is_command("/free_talk futebol") is True
        assert handler.is_command("texto normal") is False

    def test_reply_message_regular_message(
        self,
        handler: FreeTalkHandler,
        ai_tutor_service_mock,
        redis_service_mock,
        message_history_service_mock,
        user_model,
        initialized_session,
    ) -> None:
        redis_service_mock.has_lock_global_ia.return_value = False
        message_history_service_mock.get_message_history.return_value = []
        ai_tutor_service_mock.get_tutor_response.return_value = "resposta"

        response = handler.reply_message(
            phone=DEFAULT_PHONE,
            message="hello",
            session=initialized_session,
            user=user_model,
        )

        assert response == "resposta"
        ai_tutor_service_mock.get_tutor_response.assert_called_once_with(
            instruction="instruction",
            history=[],
            message="hello",
        )
        message_history_service_mock.save_messages.assert_called_once_with(
            user_id="user-1",
            phone=DEFAULT_PHONE,
            user_message="hello",
            session=initialized_session,
            tutor_message="resposta",
        )

    def test_reply_message_command_starts_session(
        self,
        handler: FreeTalkHandler,
        ai_tutor_service_mock,
        redis_service_mock,
        message_history_service_mock,
        session_service_mock,
        user_model,
        initialized_session,
    ) -> None:
        started_session = Mock(id="session-1", status=ConversationSessionsState.PRACTICING)
        session_service_mock.set_start_session_free_talk.return_value = started_session
        redis_service_mock.has_lock_global_ia.return_value = False
        message_history_service_mock.get_message_history.return_value = []
        ai_tutor_service_mock.get_tutor_response.return_value = "ok"

        response = handler.reply_message(
            phone=DEFAULT_PHONE,
            message="/free_talk esporte",
            session=initialized_session,
            user=user_model,
        )

        assert response == "ok"
        session_service_mock.set_start_session_free_talk.assert_called_once_with(
            phone=DEFAULT_PHONE,
            session=initialized_session,
            context_summary="esporte",
        )

    def test_reply_message_raises_if_global_lock(
        self,
        handler: FreeTalkHandler,
        redis_service_mock,
        user_model,
        initialized_session,
    ) -> None:
        redis_service_mock.has_lock_global_ia.return_value = True

        with pytest.raises(GlobalIALockError):
            handler.reply_message(
                phone=DEFAULT_PHONE,
                message="hello",
                session=initialized_session,
                user=user_model,
            )

    def test_reply_message_raises_if_command_without_topic(
        self,
        handler: FreeTalkHandler,
        user_model,
        initialized_session,
    ) -> None:
        with pytest.raises(RuntimeError):
            handler.reply_message(
                phone=DEFAULT_PHONE,
                message="/free_talk",
                session=initialized_session,
                user=user_model,
            )

    def test_reply_message_raises_if_session_is_practicing(
        self,
        handler: FreeTalkHandler,
        user_model,
        practicing_session,
    ) -> None:
        with pytest.raises(SessionActiveError):
            handler.reply_message(
                phone=DEFAULT_PHONE,
                message="/free_talk esporte",
                session=practicing_session,
                user=user_model,
            )

    def test_reply_message_raises_if_session_state_invalid(
        self,
        handler: FreeTalkHandler,
        user_model,
        invalid_session,
    ) -> None:
        with pytest.raises(SessionStateInvalidError):
            handler.reply_message(
                phone=DEFAULT_PHONE,
                message="/free_talk esporte",
                session=invalid_session,
                user=user_model,
            )
