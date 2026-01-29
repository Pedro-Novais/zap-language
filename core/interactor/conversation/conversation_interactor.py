from core.interface import AITutorService
from .prompts import PROMPT_MAP


class ConversationInteractor:
    
    def __init__(
        self, 
        ai_tutor_service: AITutorService, 
        zapi_service,
    ) -> None:
        
        self.ai_tutor_service = ai_tutor_service
        self.zapi_service = zapi_service

    def execute(
        self, 
        message: str,
        phone: str = "5511967599269"
    ) -> str:
        # 1. Recuperar histórico (TODO: Implementar repositório de banco de dados)
        # Por enquanto, vamos enviar vazio, o que faz a IA tratar cada msg como nova (sem memória)
        history = None
        student_level = 1
        instruction = PROMPT_MAP[1]

        # 3. Obtém resposta da IA
        ai_response = self.ai_tutor_service.get_tutor_response(
            instruction=instruction,
            history=history,
            message=message,
        )

        # 3. Enviar resposta para o usuário via Z-API
        # try:
        #     self.zapi_service.send_text(
        #         phone=phone,
        #         message=ai_response
        #     )
        # except Exception as e:
        #     print(f"Erro ao enviar mensagem via Z-API: {e}")
            
        return ai_response
        
        # 4. Salvar novo par de mensagens no banco (TODO)
        # save_history(phone, user_msg=message_text, ai_msg=ai_response)