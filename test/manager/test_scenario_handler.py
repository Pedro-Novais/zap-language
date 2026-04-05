from unittest.mock import Mock

import pytest

from core.manager.factory.handlers.scenario_handler import ScenarioHandler
from core.manager.services.conversation_session_service import ConversationSessionService
from core.manager.services.scenario_service import ScenarioService
from core.model.enum import ConversationSessionsState
from core.shared.errors import GlobalIALockError, SessionActiveError, SessionStateInvalidError


DEFAULT_PHONE = "5511999999999"


class TestScenarioHandler:

    @pytest.fixture
    def session_service_mock(self) -> ConversationSessionService:
        return Mock(spec=ConversationSessionService)

    @pytest.fixture
    def scenario_service_mock(self) -> ScenarioService:
        return Mock(spec=ScenarioService)

    @pytest.fixture
    def handler(
        self,
        ai_tutor_service_mock,
        redis_service_mock,
        message_history_service_mock,
        session_service_mock,
        scenario_service_mock,
    ) -> ScenarioHandler:
        handler = ScenarioHandler(
            ai_tutor_service=ai_tutor_service_mock,
            redis_service=redis_service_mock,
            message_history_service=message_history_service_mock,
            session_service=session_service_mock,
            scenario_service=scenario_service_mock,
        )
        handler.instruction_builder.build_scenario_instruction = Mock(return_value="instruction")
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

    @pytest.fixture
    def scenario_model(self):
        return Mock(title="Aeroporto", context="Check-in", teacher_char="Atendente")

    def test_is_command(self, handler: ScenarioHandler) -> None:
        assert handler.is_command("/scenario aeroporto") is True
        assert handler.is_command("texto normal") is False

    def test_reply_message_regular_message(
        self,
        handler: ScenarioHandler,
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

    def test_reply_message_command_starts_scenario(
        self,
        handler: ScenarioHandler,
        ai_tutor_service_mock,
        redis_service_mock,
        message_history_service_mock,
        session_service_mock,
        scenario_service_mock,
        user_model,
        initialized_session,
        scenario_model,
    ) -> None:
        started_session = Mock(id="session-1", status=ConversationSessionsState.PRACTICING)
        session_service_mock.set_start_session_scenario.return_value = started_session
        scenario_service_mock.get_by_key.return_value = scenario_model
        redis_service_mock.has_lock_global_ia.return_value = False
        message_history_service_mock.get_message_history.return_value = []
        ai_tutor_service_mock.get_tutor_response.return_value = "ok"

        response = handler.reply_message(
            phone=DEFAULT_PHONE,
            message="/scenario aeroporto",
            session=initialized_session,
            user=user_model,
        )

        assert response == "ok"
        scenario_service_mock.get_by_key.assert_called_once_with(key="aeroporto")
        session_service_mock.set_start_session_scenario.assert_called_once_with(
            phone=DEFAULT_PHONE,
            session=initialized_session,
            scenario=scenario_model,
        )

    def test_reply_message_raises_if_global_lock(
        self,
        handler: ScenarioHandler,
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

    def test_reply_message_raises_if_command_without_key(
        self,
        handler: ScenarioHandler,
        user_model,
        initialized_session,
    ) -> None:
        with pytest.raises(Exception):
            handler.reply_message(
                phone=DEFAULT_PHONE,
                message="/scenario",
                session=initialized_session,
                user=user_model,
            )

    def test_reply_message_raises_if_scenario_not_found(
        self,
        handler: ScenarioHandler,
        scenario_service_mock,
        user_model,
        initialized_session,
    ) -> None:
        scenario_service_mock.get_by_key.return_value = None

        with pytest.raises(Exception):
            handler.reply_message(
                phone=DEFAULT_PHONE,
                message="/scenario inexistente",
                session=initialized_session,
                user=user_model,
            )

    def test_reply_message_raises_if_session_is_practicing(
        self,
        handler: ScenarioHandler,
        user_model,
        practicing_session,
    ) -> None:
        with pytest.raises(SessionActiveError):
            handler.reply_message(
                phone=DEFAULT_PHONE,
                message="/scenario aeroporto",
                session=practicing_session,
                user=user_model,
            )

    def test_reply_message_raises_if_session_state_invalid(
        self,
        handler: ScenarioHandler,
        user_model,
        invalid_session,
    ) -> None:
        with pytest.raises(SessionStateInvalidError):
            handler.reply_message(
                phone=DEFAULT_PHONE,
                message="/scenario aeroporto",
                session=invalid_session,
                user=user_model,
            )
