from typing import (
    Any, 
    Dict,
)

from external.repositories import UserRepositoryImpl
from external.services import (
    AITutorService,
    ZApiService,
)
from core.interactor import ConversationInteractor


class ZapiController:
    
    def __init__(
        self,
    ) -> None:

        self.user_repository = UserRepositoryImpl()
        
        self.ai_tutor_service = AITutorService()
        self.zapi_service = ZApiService()
        
        self.conversation_interactor = ConversationInteractor(
            ai_tutor_service=self.ai_tutor_service,
            zapi_service=self.zapi_service,
        )

    def receive_message(
        self,
        message: str,
    ) -> str:

        return self.conversation_interactor.execute(
            message=message,
        )
