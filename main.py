from fastapi import FastAPI
from core.configs import settings
from api.v1.api import api_router
from core.database import Base, engine

# Importa todos os modelos para registrar na memória do SQLAlchemy
import models 

# Cria todas as tabelas no banco de dados (se ainda não existirem)
Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.PROJECT_NAME)

app.include_router(api_router, prefix=settings.API_V1_STR)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, log_level="info", reload=True)