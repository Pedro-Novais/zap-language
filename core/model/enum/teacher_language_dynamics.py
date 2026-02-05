from enum import StrEnum


class TeacherLanguageDynamics(StrEnum):
    IMMERSION = "immersion"
    BILINGUE = "bilingue"
    SUPPORT = "support"
    
    def get_language_dynamics_instruction(self) -> str:
        
        match self:
            case TeacherLanguageDynamics.IMMERSION:
                return (
                    "PROIBIDO usar português. Se o usuário falar em português, sua resposta deve ser: "
                    "1. Traduzir o que ele disse para o inglês entre aspas. 2. Responder à pergunta dele 100% em inglês."
                )
            case TeacherLanguageDynamics.BILINGUE:
                return (
                    "Padrão de resposta: [Texto em Inglês] seguido de [Tradução em Português em itálico]. "
                    "Garanta que o aluno veja a tradução de cada frase importante para acelerar a compreensão."
                )
            case TeacherLanguageDynamics.SUPPORT:
                return (
                    "Idioma principal: Inglês. Use o português EXCLUSIVAMENTE para explicar erros gramaticais complexos, "
                    "nuances culturais ou quando o aluno demonstrar confusão total."
                )
            case _:
                return "Alterne entre inglês e português conforme a necessidade da conversa."
