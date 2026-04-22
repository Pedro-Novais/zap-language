from typing import Optional

from external.database.models import CodeVerification
from external.database.connection import get_db_session
from core.interface.repository import PhoneVerificationRepository
from core.model import PhoneVerificationModel


class PhoneVerificationRepositoryImpl(PhoneVerificationRepository):
    
    def create_verification_code(
        self,
        user_id: str,
        phone_number: Optional[str],
        code: str,
        code_type: str = "PHONE",
    ) -> None:
        
        with get_db_session() as session:
            phone_verification = CodeVerification(
                user_id=user_id,
                value=phone_number if phone_number is not None else None,
                code=code,
                code_type=code_type,
            )
            session.add(phone_verification)
            session.commit()
            return

    def get_verification_code_information(
        self,
        user_id: str,
        phone_number: Optional[str],
        code_type: str = "PHONE",
    ) -> Optional[PhoneVerificationModel]:
        
        with get_db_session() as session:
            query = session.query(CodeVerification).filter(
                CodeVerification.user_id == user_id,
                CodeVerification.code_type == code_type,
            )
            if phone_number is not None:
                query = query.filter(CodeVerification.value == phone_number)

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
    ) -> None:
        
        with get_db_session() as session:
            phone_verification = session.query(CodeVerification).filter(
                CodeVerification.user_id == user_id,
            ).all()
            if not phone_verification:
                return
            
            for instance in phone_verification:
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
        