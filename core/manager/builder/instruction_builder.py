from typing import (
    List, 
    Optional,
)

from core.model import UserModel


class InstructionBuilder:
    def __init__(self) -> None:
        
        self.base_instruction = (
            "Você é um tutor de inglês especializado em conversação via WhatsApp. "
            "Seu objetivo é ajudar o aluno a praticar de forma natural e eficiente."
        )

    def build(
        self, 
        user: UserModel,
    ) -> Optional[List[str]]:

        settings = user.study_settings
        if not settings:
            return None

        persona_text = settings.persona_type.get_instruction_by_persona_type()
        dynamic_text = settings.language_dynamics.get_language_dynamics_instruction()
        topics = ", ".join(settings.preferred_topics) if settings.preferred_topics else "assuntos gerais"
        topics_text = f"Sempre que possível, direcione a conversa para os interesses do aluno: {topics}."
        correction_text = f"O nível de rigor com erros gramaticais deve ser de {settings.correction_level} baseado em uma escala máxima de 3."
        
        full_prompt = [
            self.base_instruction,
            f"DIRETRIZ DE PERSONALIDADE: {persona_text}",
            f"DINÂMICA DE AULA: {dynamic_text}",
            f"CONTEXTO DO ALUNO: {topics_text}",
            f"RIGOR DE CORREÇÃO: {correction_text}",
            "IMPORTANTE: Mantenha as mensagens curtas e adequadas para leitura no WhatsApp."
        ]
        return full_prompt
    