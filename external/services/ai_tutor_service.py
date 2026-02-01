from typing import (
    List, 
    Optional,
)

from loguru import logger
from google import genai
from google.genai.types import (
    HttpOptions, 
    Content, 
    GenerateContentConfig,
    Part,
)

from core.interface.service import AITutorService
from core.model import MessageHistoryModel


class AITutorService(AITutorService):
    
    def __init__(self) -> None:
        
        self.client = genai.Client(
            http_options=HttpOptions(
                headers={
                    "X-Vertex-AI-LLM-Request-Type": "shared"
                },
            )
        )
        self.model_id = "gemini-2.0-flash-lite" 

    def get_tutor_response(
        self,
        message: str,
        instruction: str, 
        history: Optional[List[MessageHistoryModel]],
    ) -> str:
        
        try:
            logger.info("Getting tutor response...")
            contents = self._build_content_messages(
                message=message,
                history=history,
            )
            config = self._build_content_configs(
                system_instruction=instruction,
            )
            logger.info("Sending request to motor de IA...")
            response = self.client.models.generate_content(
                model=self.model_id,
                contents=contents,
                config=config
            )
            
            return response.text
        
        except Exception as e:
            logger.error(f"Error getting tutor response: {e}")
            return "I'm having a little brain fog today. Can you repeat? 🍎"
    
    @staticmethod
    def _build_content_messages(
        message: str,
        history: Optional[List[MessageHistoryModel]],
    ) -> Content:
        
        logger.info("Building content messages...")
        contents = []
        if history:
            for item in history:
                content = Content(
                    role=item.role,
                    parts=[Part(text=item.content)]
                )
                contents.append(content)
            
        contents.append(Content(role="user", parts=[Part(text=message)]))
        return contents
    
    @staticmethod
    def _build_content_configs(
        system_instruction: str
    ) -> Content:
        
        logger.info("Building content configs...")
        config = GenerateContentConfig(
            system_instruction=system_instruction
        )
            
        return config
        