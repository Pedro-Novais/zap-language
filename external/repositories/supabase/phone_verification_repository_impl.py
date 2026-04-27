from typing import Optional

from external.database.models import CodeVerification
from external.database.connection import get_db_session
from core.interface.repository import PhoneVerificationRepository
from core.model import PhoneVerificationModel
from core.model.enum.verification_code_type import VerificationCodeType


class PhoneVerificationRepositoryImpl(PhoneVerificationRepository):
    
    def create_verification_code(
        self,
        user_id: str,
        value: Optional[str],
        code: str,
        code_type: VerificationCodeType = VerificationCodeType.PHONE,
    ) -> None:
        
        with get_db_session() as session:
            phone_verification = CodeVerification(
                user_id=user_id,
                value=value if value is not None else None,
                code=code,
                code_type=code_type,
            )
            session.add(phone_verification)
            session.commit()
            return

    def get_verification_code_information(
        self,
        user_id: str,
        value: Optional[str],
        code_type: VerificationCodeType = VerificationCodeType.PHONE,
    ) -> Optional[PhoneVerificationModel]:
        
        with get_db_session() as session:
            query = session.query(CodeVerification).filter(
                CodeVerification.user_id == user_id,
                CodeVerification.code_type == code_type,
            )
            if value is not None:
                query = query.filter(CodeVerification.value == value)

            phone_verification = query.first()
            
            if phone_verification is None:
                return None

            return PhoneVerificationModel(
                id=phone_verification.id,
                user_id=phone_verification.user_id,
                value=phone_verification.value,
                code=phone_verification.code,
                attempts=phone_verification.attempts,
                expires_at=phone_verification.expires_at,
                created_at=phone_verification.created_at,
                code_type=phone_verification.code_type,
            )
    
    def delete_old_verification_code(
        self,
        user_id: str,
        code_type: VerificationCodeType | None = None,
    ) -> None:
        with get_db_session() as session:
            query = session.query(CodeVerification).filter(
                CodeVerification.user_id == user_id,
            )
            if code_type is not None:
                query = query.filter(CodeVerification.code_type == code_type)
            phone_verifications = query.all()
            if not phone_verifications:
                return
            for instance in phone_verifications:
                session.delete(instance)
            session.commit()
            return
        
    def set_attempts_in_verification_code(
        self,
        code_id: str,
        attempts: int,
    ) -> None:
        
        with get_db_session() as session:
            session.query(CodeVerification).filter(
                CodeVerification.id == code_id,
            ).update({
                CodeVerification.attempts: attempts,
            })
            session.commit()
            return
        
    def get_verification_by_code(
        self,
        code: str,
        code_type: VerificationCodeType = VerificationCodeType.PHONE,
    ) -> Optional[PhoneVerificationModel]:
        with get_db_session() as session:
            phone_verification = session.query(CodeVerification).filter(
                CodeVerification.code == code,
                CodeVerification.code_type == code_type,
            ).first()

            if phone_verification is None:
                return None

            return PhoneVerificationModel(
                id=phone_verification.id,
                user_id=phone_verification.user_id,
                value=phone_verification.value,
                code=phone_verification.code,
                attempts=phone_verification.attempts,
                expires_at=phone_verification.expires_at,
                created_at=phone_verification.created_at,
                code_type=phone_verification.code_type,
            )
        