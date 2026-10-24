import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()

class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "API Eventos Acadêmicos"
    DB_URL: str = os.getenv("DATABASE_URL", "postgresql://postgres:sua_senha@localhost:5433/gerenciador_eventos")

    class Config:
        case_sensitive = True

settings = Settings()