from enum import IntEnum


class TeacherCorrectionLevel(IntEnum):
    LIGHT = 1
    MEDIUM = 2
    STRONG = 3
    
    def get_correction_instruction(self) -> str:
        
        match self:
            case TeacherCorrectionLevel.LIGHT:
                return (
                    "Light correction: 100% priority on fluency. Ignore minor typos or preposition "
                    "mistakes if the message is clear. Only correct the student if the error "
                    "changes the meaning or is extremely basic (e.g., 'I goes'). Stay conversational."
                )
            case TeacherCorrectionLevel.MEDIUM:
                return (
                    "Moderate correction: The standard learning balance. Respond to the student "
                    "naturally first. At the end of your message, point out 1 or 2 key grammar "
                    "or vocabulary mistakes. Use an encouraging tone and show the correct version in **bold**."
                )
            case TeacherCorrectionLevel.STRONG:
                return (
                    "Strong correction: Full focus on precision. Do not let any mistake pass. "
                    "Correct grammar, punctuation, and word choices (collocations). Briefly explain "
                    "the correction, but keep the conversation moving. Use a non-intrusive format like bullet points at the end."
                )
            case _:
                return "Maintain a natural balance between conversation and correction."
            