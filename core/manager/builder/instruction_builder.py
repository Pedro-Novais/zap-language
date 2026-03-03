from typing import (
    List, 
    Optional,
)

from core.model import UserModel
from core.model.enum import UserLevelLanguage


class InstructionBuilder:
    def __init__(self) -> None:
        
        self.base_instruction = (
            "Você é um tutor de inglês especializado em conversação via WhatsApp. "
            "Seu objetivo é ajudar o aluno a praticar de forma natural e eficiente."
            "Sempre responda ao comentário/pergunta do aluno primeiro para manter a conversa fluindo."
            "Respostas curtas e escaneáveis (máx 3 parágrafos)."
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
        
        user_preferred_topics = ", ".join(settings.preferred_topics) if settings.preferred_topics else "Assuntos Gerais"
        current_topic = user.current_topic if user.current_topic else "Assuntos Gerais"
        
        user_level_text = self.user_level.get_user_level_language_instruction()
        persona_text = settings.persona_type.get_instruction_by_persona_type()
        dynamic_text = settings.language_dynamics.get_language_dynamics_instruction()
        gramamatical_rigor = settings.correction_level.get_correction_instruction()
        
        full_prompt = [
            self.base_instruction,
            f"### CONTEXTO DO ALUNO\n"
            f"O aluno se interessa por: {user_preferred_topics}. "
            f"A cada 3 a 6 interações, use exemplos ou analogias baseadas nesses interesses para tornar o aprendizado mais engajador."
            f"### NÍVEL DO ALUNO\n {user_level_text}",
            f"### PERFIL DO TUTOR\n {persona_text}",
            f"### MÉTODO DE ENSINO\n {dynamic_text}",
            f"### RIGOR GRAMATICAL\n {gramamatical_rigor}",
            f"### TÓPICO ATUAL DA CONVERSA\n Assunto: {current_topic}. "
        ]
        return full_prompt
    