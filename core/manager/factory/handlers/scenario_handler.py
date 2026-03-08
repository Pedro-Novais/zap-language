from core.manager.factory.handlers import ConversationHandler
from core.model import ConversationSessionModel


class ScenarioHandler(ConversationHandler):
    def __init__(self) -> None:
        pass
    
    def process_message(
        self, 
        phone: str, 
        message: str,
        session: ConversationSessionModel,
    ) -> None:
        
        pass
    