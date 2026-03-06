from enum import StrEnum


class TeacherLanguageDynamics(StrEnum):
    IMMERSION = "immersion"
    BILINGUE = "bilingue"
    SUPPORT = "support"
    
    def get_language_dynamics_instruction(self) -> str:
        
        match self:
            case TeacherLanguageDynamics.IMMERSION:
                return (
                    "FORBIDDEN: Do not use Portuguese in your explanations. If the student speaks in Portuguese, "
                    "simply rephrase their sentence in English: 'Oh, you mean: \"[English sentence]\"' "
                    "and keep the conversation flowing naturally."
                )
            case TeacherLanguageDynamics.BILINGUE:
                return (
                    "Always respond in English first. Immediately below, provide a natural translation "
                    "into Portuguese. Use a clear visual separator like '--- Translation:'."
                )
            case TeacherLanguageDynamics.SUPPORT:
                return (
                    "Speak English 90% of the time. Use Portuguese only as a last resort "
                    "to explain concepts the student failed to understand after two attempts in English."
                )
