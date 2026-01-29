from typing import Optional

from external.database.models._User import User
from external.database.connection import get_db_session
from core.interface.repository import UserRepository


class UserRepositoryImpl(UserRepository):

    def create(
        self, 
        name: str,
        email: str,
        password_hash: str,
    ) -> None:

        with get_db_session() as session:
            user = User(
                email=email,
                name=name,
                password=password_hash,
            )
            session.add(user)
            session.commit()
            session.refresh(user)
            return
        
    def get_user_by_id(
        self, 
        user_id: str,
    ) -> Optional[User]:
        
        with get_db_session() as session:
            return session.query(User).filter(User.id == user_id).first()
        
    def get_user_by_email(
        self, 
        email: str,
    ) -> Optional[User]:
        
        with get_db_session() as session:
            user = session.query(User).filter(User.email == email).first()
            return user
        