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
        password: str, 
        password_hash: str,
    ) -> bool:
        
        return bcrypt.checkpw(
            password.encode(),
            password_hash.encode()
        )
