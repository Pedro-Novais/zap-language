from enum import StrEnum


class TeacherLanguageDynamics(StrEnum):
    IMMERSION = "immersion"
    BILINGUE = "bilingue"
    SUPPORT = "support"
    
    def get_language_dynamics_instruction(self) -> str:
        
        match self:
            case TeacherLanguageDynamics.IMMERSION:
                return (
                    "PROIBIDO usar português nas suas explicações. Se o usuário falar em português, "
                    "reformula a frase dele em inglês: 'Oh, you mean: \"[English sentence]\"' e siga a conversa."
                )
            case TeacherLanguageDynamics.BILINGUE:
                return (
                    "Responda primeiro em inglês. Logo abaixo, forneça uma tradução fluida para o português. "
                    "Use um separador visual como '--- Tradução:'."
                )
            case TeacherLanguageDynamics.SUPPORT:
                return (
                    "Fale inglês 90% do tempo. Use o português apenas como último recurso para "
                    "explicar conceitos que o aluno não entendeu após duas tentativas em inglês."
                )
