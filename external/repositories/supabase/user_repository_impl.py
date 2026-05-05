from datetime import datetime
from typing import Optional

from sqlalchemy.orm import joinedload

from external.database.models._User import User
from external.database.connection import get_db_session
from core.interface.repository import UserRepository
from core.model import UserModel, StudySettingsModel


class UserRepositoryImpl(UserRepository):

    def create(
        self, 
        name: str,
        email: str,
        password_hash: str,
    ) -> UserModel:

        with get_db_session() as session:
            user = User(
                email=email,
                name=name,
                password=password_hash,
            )
            session.add(user)
            session.commit()
            session.refresh(user)
            return self._transform_user_data_in_user_model(user=user)

    def create_google_user(
        self,
        name: str,
        email: str,
        sub: str,
        password_hash: str,
        last_login: datetime,
    ) -> UserModel:

        with get_db_session() as session:
            user = User(
                email=email,
                name=name,
                sub=sub,
                password=password_hash,
                last_login=last_login,
                is_valid=True,
            )
            session.add(user)
            session.commit()
            session.refresh(user)
            return self._transform_user_data_in_user_model(user=user)
        
    def get_user_by_id(
        self, 
        user_id: str,
    ) -> Optional[UserModel]:
        
        with get_db_session() as session:
            user = session.query(User).filter(User.id == user_id).first()
            return self._transform_user_data_in_user_model(user=user)
        
    def get_safe_user_by_id(
        self, 
        user_id: str,
    ) -> Optional[UserModel]:
        
        with get_db_session() as session:
            user = session.query(User).filter(User.id == user_id).first()
            return self._transform_user_data_in_user_model(user=user)

    def get_user_by_email(
        self, 
        email: str,
    ) -> Optional[UserModel]:
        
        with get_db_session() as session:
            user = session.query(User).filter(User.email == email).first()
            return self._transform_user_data_in_user_model(user=user)
    
    def get_user_by_phone_number(
        self, 
        phone: str,
    ) -> Optional[UserModel]:
        
        with get_db_session() as session:
            user = session.query(User).options(
                joinedload(User.study_settings)
            ).filter(User.phone == phone).first()
            return self._transform_user_data_in_user_model(user=user)
    
    def get_user_by_sub(
        self,
        sub: str,
    ) -> Optional[UserModel]:

        with get_db_session() as session:
            user = session.query(User).filter(User.sub == sub).first()
            return self._transform_user_data_in_user_model(user=user)
    
    def get_phone_number_by_user_id(
        self, 
        user_id: str,
    ) -> Optional[str]:
        
        with get_db_session() as session:
            user = session.query(User).filter(User.id == user_id).first()
            return user.phone if user else None
        
    def insert_phone_number_by_user_id(
        self, 
        user_id: str,
        phone_number: str,
    ) -> None:
        
        with get_db_session() as session:
            user = session.query(User).filter(User.id == user_id).first()
            user.phone = phone_number
            user.whatsapp_enabled = True
            session.commit()
            return
    
    def update_password(
        self, 
        user_id: str,
        new_password_hash: str,
    ) -> None:
        
        with get_db_session() as session:
            user = session.query(User).filter(User.id == user_id).first()
            user.password = new_password_hash
            session.commit()
            return

    def update_google_login(
        self,
        user_id: str,
        sub: str,
        last_login: datetime,
    ) -> UserModel:

        with get_db_session() as session:
            user = session.query(User).filter(User.id == user_id).first()
            user.sub = sub
            user.last_login = last_login
            session.commit()
            session.refresh(user)
            return self._transform_user_data_in_user_model(user=user)

    def update_payment_customer_id(
        self,
        user_id: str,
        payment_customer_id: str,
    ) -> None:

        with get_db_session() as session:
            user = session.query(User).filter(User.id == user_id).first()
            if user:
                user.payment_customer_id = payment_customer_id
                session.commit()
            return
    
    @staticmethod
    def _transform_user_data_in_user_model(
        user: Optional[User],
    ) -> Optional[UserModel]:
        
        if not user:
            return None
    
        study_settings = user.study_settings
        study_settings_model = None
        if study_settings:
            study_settings_model = StudySettingsModel(
                id=study_settings.id,
                user_id=study_settings.user_id,
                persona_type=study_settings.persona_type,
                correction_level=study_settings.correction_level,
                preferred_topics=study_settings.preferred_topics,
                language_ratio=study_settings.language_ratio,
                language_dynamics=study_settings.language_dynamics,
                receive_newsletters=study_settings.receive_newsletters,
                preferred_language=study_settings.preferred_language,
                created_at=study_settings.created_at,
            )
            
        return UserModel(
            id=user.id,
            email=user.email,
            name=user.name,
            phone=user.phone,
            whatsapp_enabled=user.whatsapp_enabled,
            is_valid=user.is_valid,
            is_admin=user.is_admin,
            created_at=user.created_at,
            google_id=user.google_id,
            sub=user.sub,
            last_login=user.last_login,
            payment_customer_id=user.payment_customer_id,
            study_settings=study_settings_model,
            password=user.password,
        )

    def update_is_valid(
        self, 
        user_id: str,
        is_valid: bool,
    ) -> None:
        
        with get_db_session() as session:
            user = session.query(User).filter(User.id == user_id).first()
            
            if user:
                user.is_valid = is_valid
                session.commit()
            
            return
        