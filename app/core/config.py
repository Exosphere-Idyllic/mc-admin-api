from pydantic_settings import BaseSettings
from typing import List
from functools import lru_cache


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "Minecraft Admin Panel"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # JWT
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 60
    
    # RCON
    RCON_HOST: str = "127.0.0.1"
    RCON_PORT: int = 25575
    RCON_PASSWORD: str
    
    # Services
    MINECRAFT_SERVICE: str = "minecraft"
    PLAYIT_SERVICE: str = "playit"
    
    # Database
    DATABASE_URL: str = "sqlite:///./data/admin.db"
    
    # CORS (como lista de strings)
    CORS_ORIGINS: str = '["http://localhost:3000"]'
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Convierte string JSON a lista"""
        import json
        try:
            return json.loads(self.CORS_ORIGINS)
        except:
            return ["http://localhost:3000"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()