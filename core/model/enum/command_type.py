from enum import StrEnum
    

class CommandTypeSet(StrEnum):
    
    RESET = "reset"
    SCENARIO = "scenario"
    

class CommandType(StrEnum):

    TRANSLATE = "translate"
    TUTOR = "tutor"
    HELP = "help"
    END_SESSION = "end"
