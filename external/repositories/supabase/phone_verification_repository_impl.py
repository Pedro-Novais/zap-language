from typing import Optional

from external.database.models import PhoneVerification
from external.database.connection import get_db_session
from core.interface.repository import PhoneVerificationRepository
from core.model import PhoneVerificationModel


class PhoneVerificationRepositoryImpl(PhoneVerificationRepository):
    
    def create_verification_code(
        self,
        user_id: str,
        phone_number: str,
        code: str,
    ) -> None:
        
        with get_db_session() as session:
            phone_verification = PhoneVerification(
                user_id=user_id,
                phone_number=phone_number,
                code=code,
            )
            session.add(phone_verification)
            session.commit()
            return

    def get_verification_code_information(
        self,
        user_id: str,
        phone_number: str,
    ) -> Optional[PhoneVerificationModel]:
        
        with get_db_session() as session:
            phone_verification = session.query(PhoneVerification).filter(
                PhoneVerification.user_id == user_id,
                PhoneVerification.phone_number == phone_number,
            ).first()
            
            if phone_verification is None:
                return None

            return PhoneVerificationModel(
                id=phone_verification.id,
                user_id=phone_verification.user_id,
                phone_number=phone_verification.phone_number,
                code=phone_verification.code,
                attempts=phone_verification.attempts,
                expires_at=phone_verification.expires_at,
                created_at=phone_verification.created_at,
            )
    
    def delete_old_verification_code(
        self,
        user_id: str,
    ) -> None:
        
        with get_db_session() as session:
            phone_verification = session.query(PhoneVerification).filter(
                PhoneVerification.user_id == user_id,
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
            session.query(PhoneVerification).filter(
                PhoneVerification.id == code_id,
            ).update({
                PhoneVerification.attempts: attempts,
            })
            session.commit()
            return
        