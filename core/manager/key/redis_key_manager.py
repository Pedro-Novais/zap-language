class RedisKeyManager:
    
    PREFIX = "zap_lang"

    @classmethod
    def processing_phone(
        cls, 
        phone: str,
    ) -> str:
        return f"{cls.PREFIX}:processing:{phone}"
    
    @classmethod
    def rate_limit_phone(
        cls, 
        phone: str,
    ) -> str:
        return f"{cls.PREFIX}:rate_limit:{phone}"
    
    @classmethod
    def ai_health_status(
        cls, 
    ) -> str:
        return f"{cls.PREFIX}:ai_health_status"
    
    @classmethod
    def user_history(
        cls, 
        phone: str,
    ) -> str:
        return f"{cls.PREFIX}:history:{phone}"
    
    @classmethod
    def black_list_phone(
        cls, 
        phone: str,
    ) -> str:
        return f"{cls.PREFIX}:blacklist:{phone}"
    
    @classmethod
    def user_profile(
        cls, 
        phone: str,
    ) -> str:
        return f"{cls.PREFIX}:profile:{phone}"
    
    @classmethod
    def update_user_profile(
        cls, 
        phone: str,
    ) -> str:
        return f"{cls.PREFIX}:profile:update:{phone}"
    