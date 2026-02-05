import os

from cryptography.fernet import Fernet

from core.interface.service import IDProtectorService


class FernetIDProtectorServiceImpl(IDProtectorService):
    
    def __init__(self):
        key = os.getenv("ID_ENCRYPTION_KEY")
        
        if not key:
            key = Fernet.generate_key().decode()
            
        self.cipher = Fernet(key.encode())

    def encrypt(
        self, 
        real_id: str,
    ) -> str:
        
        if not real_id:
            return ""
        return self.cipher.encrypt(real_id.encode()).decode()

    def decrypt(
        self, 
        encrypted_id: str,
    ) -> str:
        
        try:
            return self.cipher.decrypt(encrypted_id.encode()).decode()
        except Exception:
            raise ValueError("ID de configuração inválido ou expirado.")