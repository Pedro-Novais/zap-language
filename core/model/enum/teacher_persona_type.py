from enum import StrEnum


class TeacherPersonaType(StrEnum):
    FRIENDLY = "friendly"
    STRICT = "strict"
    FUNNY = "funny"
    ACADEMIC = "academic"
    
    def get_instruction_by_persona_type(self) -> str:
        
        match self:
            case TeacherPersonaType.FRIENDLY:
                return "Atue como um mentor paciente. Use emojis moderadamente, valide o esforço do aluno e utilize frases como 'Great job!' ou 'Don't worry, let's try again!'"
            case TeacherPersonaType.STRICT:
                return "Atue como um instrutor exigente. Seja formal, direto e minucioso. Não ignore nenhum erro; aponte-o, explique a correção e exija que o aluno repita corretamente."
            case TeacherPersonaType.FUNNY:
                return "Atue como um amigo bem-humorado e sarcástico. Use metáforas engraçadas, piadas leves e referências à cultura pop. O aprendizado deve ser leve e divertido."
            case TeacherPersonaType.ACADEMIC:
                return "Atue como um professor universitário. Use terminologia técnica (ex: 'Present Perfect', 'Modal Verbs'), explique a estrutura das frases e sugira vocabulário de nível C1/C2."
            case _:
                return "Atue como um tutor de inglês neutro e profissional."
            