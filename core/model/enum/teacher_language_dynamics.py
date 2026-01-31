from enum import StrEnum


class TeacherLanguageDynamics(StrEnum):
    IMMERSION = "immersion"
    BILINGUE = "bilingue"
    SUPPORT = "support"
    
    def get_language_dynamics_instruction(self) -> str:
        match self:
            case TeacherLanguageDynamics.IMMERSION:
                return (
                    "Fale 100% em inglês. Se o usuário falar em português, não responda em português; "
                    "em vez disso, reescreva a dúvida dele em inglês e responda em inglês para forçar a imersão."
                )
            case TeacherLanguageDynamics.BILINGUE:
                return (
                    "Para cada mensagem enviada, forneça primeiro o texto em inglês e, logo abaixo, "
                    "a tradução literal ou contextual para o português entre parênteses ou em um novo parágrafo."
                )
            case TeacherLanguageDynamics.SUPPORT:
                return (
                    "O idioma principal da conversa é o inglês. No entanto, se você precisar explicar "
                    "regras gramaticais complexas, gírias ou erros do usuário, use o português para garantir o entendimento."
                )
            case _:
                return "Mantenha uma conversa equilibrada entre inglês e português."