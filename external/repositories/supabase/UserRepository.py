from external.database.connection import get_db_session

class UserRepository:
    def create(self, user):
        with get_db_session() as session:
            session.add(user)
            return user
