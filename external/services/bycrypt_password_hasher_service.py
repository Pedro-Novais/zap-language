import bcrypt

from core.interface.service import PasswordHasherService


class BcryptPasswordHasherService(PasswordHasherService):

    def hash(
        self, 
        password: str,
    ) -> str:
        
        return bcrypt.hashpw(
            password.encode(),
            bcrypt.gensalt()
        ).decode()

    def verify(
        self, 
        password_sended: str,
        password_saved: str,
    ) -> bool:
        
        return bcrypt.checkpw(
            password_sended.encode(),
            password_saved.encode()
        )
