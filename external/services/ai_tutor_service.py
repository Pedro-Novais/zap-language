from typing import List, Dict, Optional

from google import genai
from google.genai.types import HttpOptions, Content, GenerateContentConfig, Part

from core.interface.service import AITutorService

class AITutorService(AITutorService):
    
    def __init__(self):
        
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
        instruction: str, 
        history: Optional[List[Dict[str, any]]],
        message: str,
    ) -> str:
        
        try:
            # 1. Montamos o conteúdo atual + histórico
            # O histórico deve vir antes da mensagem atual
            contents = []
            if history:
                for item in history:
                    contents.append(Content(
                        role=item['role'],
                        parts=[Part(text=item['parts'][0] if isinstance(item['parts'], list) else item['parts'])]
                    ))
            
            contents.append(Content(role="user", parts=[Part(text=message)]))

            response = self.client.models.generate_content(
                model=self.model_id,
                contents=message,
                config=GenerateContentConfig(
                    system_instruction=instruction
                )
            )
            
            return response.text
        
        except Exception as e:
            print(f"Erro no motor de IA: {e}")
            return "I'm having a little brain fog today. Can you repeat? 🍎"
        


            # response = self.client.models.generate_content(
            #     model=self.model_id,
            #     contents=message,