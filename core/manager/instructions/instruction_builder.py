from typing import Optional

from core.model import UserModel, ConversationSessionModel, ScenarioModel
from core.model.enum import UserLevelLanguage


DEFAULT_TOPIC = "Assuntos Gerais"


class InstructionBuilder:
    def __init__(self) -> None:
        
        self.base_instruction = (
            "You are an expert English tutor specializing in WhatsApp conversation. "
            "Your goal is to help the student practice naturally and efficiently. "
            "Keep responses short, scannable, and mobile-friendly (max 3 paragraphs). "
            "Focus on engagement—if the student's reply is brief, ask a follow-up question to keep the chat alive."
        )
        # TODO : Mudar isso para ser dinâmico de acordo com o nível do usuário
        self.user_level = UserLevelLanguage.A1

    def build_free_talk_instruction(
        self, 
        user: UserModel,
        session: ConversationSessionModel,
    ) -> Optional[str]: # Mudei para str para facilitar o envio à IA

        settings = user.study_settings
        
        # Pega o nível direto do usuário (resolvendo seu TODO)
        # level_instr = user.language_level.get_user_level_language_instruction()
        
        current_topic = session.context_description or DEFAULT_TOPIC
        
        full_prompt = [
            self.base_instruction,
            f"### STUDENT LEVEL\n{self.user_level}",
            f"### TUTOR PERSONA\n{settings.persona_type.get_instruction_by_persona_type()}",
            f"### TEACHING METHOD\n{settings.language_dynamics.get_language_dynamics_instruction()}",
            f"### GRAMMAR RIGOR\n{settings.correction_level.get_correction_instruction()}",
            "### GOLDEN RULES:\n"
            "1. CONVERSATION FIRST: React like a human (e.g., 'Oh, interesting!', 'I totally agree').\n"
            "2. NO INTERRUPTIONS: Corrections MUST go to a 'Correction Section' at the very end of the message.\n"
            "3. KEEP IT FLOWING: If the student is dry, use their context to pivot back to the topic.\n"
            "4. FORMATTING: Use bold for key terms. Max 3 short paragraphs.",
            f"### CURRENT TOPIC: {current_topic}\n"
            f"Focus your engagement around this subject. If the user asks about something else, answer briefly and bridge back to {current_topic}."
        ]
            
        return "\n\n".join(full_prompt)
    
    def build_scenario_instruction(
        self,
        user: UserModel,
        session: ConversationSessionModel,
        scenario: ScenarioModel,
    ) -> Optional[str]:

        settings = user.study_settings
        full_prompt = [
            self.base_instruction,
            f"### STUDENT LEVEL\n{self.user_level}",
            f"### TUTOR PERSONA\n{settings.persona_type.get_instruction_by_persona_type()}",
            f"### TEACHING METHOD\n{settings.language_dynamics.get_language_dynamics_instruction()}",
            f"### GRAMMAR RIGOR\n{settings.correction_level.get_correction_instruction()}",
            "### GOLDEN RULES:\n"
            "1. CONVERSATION FIRST: React like a human (e.g., 'Oh, interesting!', 'I totally agree').\n"
            "2. NO INTERRUPTIONS: Corrections MUST go to a 'Correction Section' at the very end of the message.\n"
            "3. KEEP IT FLOWING: If the student is dry, use their context to pivot back to the topic.\n"
            "4. FORMATTING: Use bold for key terms. Max 3 short paragraphs.",
            f"### SCENARIO: {scenario.key}\n"
            f"**Context:** {scenario.description}\n"
            f"**Your Character:** {scenario.ai_role_definition}\n"
            f"**Student Character:** {scenario.user_role_definition}\n"
            "---"
            "You must strictly follow the scenario. Guide the user through the context and objectives. "
            "Always respond in character."
        ]

        return "\n\n".join(full_prompt)
    