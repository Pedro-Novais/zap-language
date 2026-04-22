from enum import Enum


class VerificationCodeType(str, Enum):
    PHONE = "PHONE"
    NUMBER = "NUMBER"
    EMAIL = "EMAIL"
