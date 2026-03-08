from enum import StrEnum
    

class CommandTypeSet(StrEnum):
    
    RESET = "reset"
    SCENARIO = "scenario"
    

class CommandTypeGet(StrEnum):

    TRANSLATE = "translate"
    TUTOR = "tutor"
    HELP = "help"
