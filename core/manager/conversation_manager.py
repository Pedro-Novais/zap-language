import logging

from core.interactor.conversation import PROMPT_MAP
from core.interface.service import (
    AITutorService,
    WhatsappService,
)
from core.interface.repository import UserRepository


logger = logging.getLogger(__name__)

class ConversationManager:
    
    def __init__(
        self,
        user_repository: UserRepository, 
        ai_tutor_service: AITutorService, 
        whatsapp_service: WhatsappService,
    ) -> None:
        
        self.user_repository = user_repository
        # self.history_repo = history_repo
        self.ai_tutor_service = ai_tutor_service
        self.whatsapp_service = whatsapp_service

    def process_and_respond(
        self, 
        phone: str, 
        message_text: str,
        ) -> None:

        # 1. Busca o usuário e histórico
        # user = self.user_repository.get_by_phone(phone)
        # history = self.history_repo.get_recent_by_user(user.id, limit=10)

        # 2. Formata o Prompt (buscando nível do usuário se necessário)
        instruction = PROMPT_MAP[1]

        # 3. Obtém resposta da IA
        message_tutor = self.ai_tutor_service.get_tutor_response(
            instruction=instruction,
            history=None,
            message=message_text,
        )
        logger.info("Resposta da IA obtida com sucesso: {}".format(message_tutor))

        # 4. Salva no histórico (User e Assistant)
        # self.history_repo.save_message(user.id, "user", message_text)
        # self.history_repo.save_message(user.id, "assistant", response)

        # 5. Envia via WhatsApp
        # self.zapi_service.send_text(
        #     phone=phone, 
        #     message=message_tutor,
        # )