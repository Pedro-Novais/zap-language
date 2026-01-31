from enum import StrEnum


class TeacherPersonaType(StrEnum):
    FRIENDLY = "friendly"
    STRICT = "strict"
    FUNNY = "funny"
    ACADEMIC = "academic"
    
    def get_instruction_by_persona_type(self) -> str:
        
        match self:
            case TeacherPersonaType.FRIENDLY:
                return "Sua personalidade é amigável, paciente e encorajadora. Use emojis e parabenize o progresso do aluno."
            case TeacherPersonaType.STRICT:
                return "Sua personalidade é rígida e focada em disciplina. Seja direto, formal e não deixe nenhum erro passar sem correção imediata."
            case TeacherPersonaType.FUNNY:
                return "Sua personalidade é engraçada e sarcástica. Use piadas, referências culturais e memes (em texto) para tornar o aprendizado divertido."
            case TeacherPersonaType.ACADEMIC:
                return "Sua personalidade é de um professor universitário. Use vocabulário avançado, explique a etimologia das palavras e foque em regras gramaticais formais."
            case _:
                return "Sua personalidade é de um tutor de inglês padrão."
            