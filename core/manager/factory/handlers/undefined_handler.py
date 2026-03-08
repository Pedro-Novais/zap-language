from core.manager.factory.handlers import ConversationHandler
from core.model import ConversationSessionModel


class UndefinedHandler(ConversationHandler):
    def __init__(self) -> None:
        pass
    
    def process_message(
        self, 
        phone: str, 
        message: str,
        session: ConversationSessionModel,
    ) -> None:
        
        pass
    
# "🌟 Nova sessão iniciada!

# Para começarmos, selecione como você deseja praticar hoje:

# 🎭 Simular um Cenário:
# Digite: /scenario [nome]
# Ex: /scenario aeroporto
# (Saia da zona de conforto simulando situações reais!)

# 🗣️ Conversa Livre:
# Digite: /free_talk [tópico]
# Ex: /free_talk futebol
# (Debata qualquer assunto com seu tutor de IA.)

# Dica: Se estiver na dúvida, apenas digite /scenarios para ver as opções disponíveis!"
    