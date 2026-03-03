from enum import StrEnum
    

class CommandTypeSet(StrEnum):
    
    RESET = "reset"
    

class CommandTypeGet(StrEnum):

    TRANSLATE = "translate"
    TUTOR = "tutor"
    HELP = "help"
