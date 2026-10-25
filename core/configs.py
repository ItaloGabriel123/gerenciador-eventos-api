import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()

class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "API Eventos Académicos"
    DB_URL: str = os.getenv("DATABASE_URL", "sqlite:///./sql_app.db")
    
    # Configurações de Segurança JWT
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "chave_secreta_super_segura_para_desenvolvimento_123456")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "120"))

    class Config:
        case_sensitive = True

settings = Settings()