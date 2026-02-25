from enum import IntEnum


class TeacherCorrectionLevel(IntEnum):
    LIGHT = 1
    MEDIUM = 2
    STRONG = 3
    
    def get_correction_instruction(self) -> str:
        
        match self:
            case TeacherCorrectionLevel.LIGHT:
                return (
                    "Tenha uma correção leve: Priorize 100% a fluidez. "
                    "Ignore erros pequenos de digitação ou preposições se a mensagem for clara. "
                    "Só corrija se o erro mudar o sentido da frase ou for algo muito básico (ex: 'I goes')."
                )
            case TeacherCorrectionLevel.MEDIUM:
                return (
                    "Tenha uma correção moderada: O padrão para aprendizado. "
                    "Responda ao aluno e, ao final, aponte 1 ou 2 erros principais de gramática ou vocabulário. "
                    "Use um tom encorajador e mostre a forma correta em negrito."
                )
            case TeacherCorrectionLevel.STRONG:
                return (
                    "Tenha uma correção forte: Foco total em precisão. "
                    "Não deixe nenhum erro passar. Corrija gramática, pontuação e escolha de palavras (collocations). "
                    "Explique brevemente por que a correção foi feita, mas mantenha o papo natural."
                )
            case _:
                return "Mantenha um equilíbrio natural entre conversa e correção."