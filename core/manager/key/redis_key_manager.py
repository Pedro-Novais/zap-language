class RedisKeyManager:
    
    PREFIX_API = "zap_lang_api"
    PREFIX_WORKER = "zap_lang_worker"

    @classmethod
    def processing_phone(
        cls, 
        phone: str,
    ) -> str:
        return f"{cls.PREFIX_WORKER}:processing:{phone}"
    
    @classmethod
    def rate_limit_phone(
        cls, 
        phone: str,
    ) -> str:
        return f"{cls.PREFIX_WORKER}:rate_limit:{phone}"
    
    @classmethod
    def user_history(
        cls, 
        phone: str,
    ) -> str:
        return f"{cls.PREFIX_WORKER}:history:{phone}"
    
    @classmethod
    def black_list_phone(
        cls, 
        phone: str,
    ) -> str:
        return f"{cls.PREFIX_WORKER}:blacklist:{phone}"
    
    @classmethod
    def user_profile(
        cls, 
        phone: str,
    ) -> str:
        return f"{cls.PREFIX_WORKER}:profile:{phone}"
    
    @classmethod
    def update_user_profile(
        cls, 
        phone: str,
    ) -> str:
        return f"{cls.PREFIX_WORKER}:profile:update:{phone}"

    @classmethod
    def queue_whatasapp_messages(
        cls, 
    ) -> str:
        return f"{cls.PREFIX_WORKER}:queue:whatsapp_messages"
    
    @classmethod
    def global_ia_lock(
        cls, 
    ) -> str:
        return f"{cls.PREFIX_WORKER}:global_ia_lock"
    
    @classmethod
    def api_user_cached(
        cls, 
        user_id: str,
    ) -> str:
        
        return f"{cls.PREFIX_API}:user_cached:{user_id}"
    