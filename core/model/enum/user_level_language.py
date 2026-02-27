from enum import StrEnum


class UserLevelLanguage(StrEnum):
    A1 = "A1"
    B2 = "B1"
    C1 = "C1"
    
    def get_user_level_language_instruction(self) -> str:
        
        match self:
            case UserLevelLanguage.A1:
                return "Use frases extremamente simples, presente do indicativo e vocabulário básico. Evite gírias ou phrasal verbs.",
            case UserLevelLanguage.B2:
                return "Pode usar termos mais técnicos, phrasal verbs comuns e tempos verbais compostos. Desafie o usuário com expressões idiomáticas."
            case UserLevelLanguage.C1:
                return "Fale como um nativo. Use vocabulário sofisticado, nuances culturais e estruturas gramaticais complexas."
            case _:
                return "Use frases extremamente simples, presente do indicativo e vocabulário básico. Evite gírias ou phrasal verbs."
            