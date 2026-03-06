from enum import StrEnum


class UserLevelLanguage(StrEnum):
    A1 = "A1"
    B2 = "B1"
    C1 = "C1"
    
    def get_user_level_language_instruction(self) -> str:
        
        match self:
            case UserLevelLanguage.A1:
                return (
                    "A1 (Beginner): Use extremely simple sentences, present tense, and basic vocabulary. "
                    "Avoid slang or complex phrasal verbs. If you use a slightly harder word, "
                    "provide the Portuguese translation in parentheses."
                )
            case UserLevelLanguage.B2:
                return (
                    "B2 (Upper-Intermediate): You can use technical terms, common phrasal verbs, and compound tenses. "
                    "Challenge the student with common idioms and encourage them to use more precise vocabulary."
                )
            case UserLevelLanguage.C1:
                return (
                    "C1 (Advanced): Speak like a native. Use sophisticated vocabulary, cultural nuances, "
                    "and complex grammatical structures. Engage in deep, nuanced discussions."
                )
            case _:
                return (
                    "A1 (Beginner): Use extremely simple sentences, present tense, and basic vocabulary. "
                    "Avoid slang or complex phrasal verbs."
                )
            