from typing import (
    List, 
    Optional,
)

from core.model import UserModel
from core.model.enum import UserLevelLanguage


DEFAULT_TOPIC = "Assuntos Gerais"


class InstructionBuilder:
    def __init__(self) -> None:
        
        self.base_instruction = (
            "You are an expert English tutor specializing in WhatsApp conversation. "
            "Your goal is to help the student practice naturally and efficiently. "
            "Always react and respond to the student's current comment/question first to keep the conversation flowing. "
            "Keep responses short, scannable, and mobile-friendly (max 3 paragraphs). "
            "Focus on engagement—if the student's reply is brief, ask a follow-up question to keep the chat alive."
        )
        # TODO : Mudar isso para ser dinâmico de acordo com o nível do usuário
        self.user_level = UserLevelLanguage.A1

    def build(
        self, 
        user: UserModel,
    ) -> Optional[List[str]]:

        settings = user.study_settings
        if not settings:
            return None
        
        user_preferred_topics = ", ".join(settings.preferred_topics) if settings.preferred_topics else DEFAULT_TOPIC
        current_topic = user.current_topic if user.current_topic else "Assuntos Gerais"
        
        user_level_text = self.user_level.get_user_level_language_instruction()
        persona_text = settings.persona_type.get_instruction_by_persona_type()
        dynamic_text = settings.language_dynamics.get_language_dynamics_instruction()
        gramamatical_rigor = settings.correction_level.get_correction_instruction()
        
        full_prompt = [
            self.base_instruction,
            f"### STUDENT CONTEXT\nInterests: {user_preferred_topics}.",
            f"### STUDENT LEVEL\n{user_level_text}",
            f"### TUTOR PERSONA\n{persona_text}",
            f"### TEACHING METHOD\n{dynamic_text}",
            f"### GRAMMAR RIGOR\n{gramamatical_rigor}",
            "### GOLDEN RULES (Top Priority):\n"
            "1. CONVERSATION FIRST: Always react to the student's message like a real person (e.g., 'Oh, cool!', 'I see').\n"
            "2. NO INTERRUPTIONS: Never start a sentence by correcting. Place corrections at the very end.\n"
            "3. KEEP IT FLOWING: If the student gives a short answer, use their interests to ask a follow-up question.\n"
            "4. FORMATTING: Use bold for new terms or essential corrections. Max 3 short paragraphs."
        ]

        if current_topic != DEFAULT_TOPIC:
            full_prompt.append(f"### TÓPICO ATUAL DA CONVERSA\n Assunto: {current_topic}. ")
            
        return full_prompt
    