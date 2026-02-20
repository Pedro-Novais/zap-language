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
            "Sempre responda ao comentário/pergunta do aluno primeiro para manter a conversa fluindo."
            "Respostas curtas e escaneáveis (máx 3 parágrafos)."
        )

    def build(
        self, 
        user: UserModel,
    ) -> Optional[List[str]]:

        settings = user.study_settings
        if not settings:
            return None
        
        current_topic = user.current_topic if user.current_topic else "Assuntos Gerais"
        
        persona_text = settings.persona_type.get_instruction_by_persona_type()
        dynamic_text = settings.language_dynamics.get_language_dynamics_instruction()
        gramamatical_rigor = settings.correction_level.get_correction_instruction()
        
        full_prompt = [
            self.base_instruction,
            f"### PERFIL DO TUTOR\n{persona_text}",
            f"### MÉTODO DE ENSINO\n{dynamic_text}",
            f"### RIGOR GRAMATICAL\n{gramamatical_rigor}",
            f"### TÓPICO DA CONVERSA\nAssunto: {current_topic}. "
        ]
        return full_prompt
    