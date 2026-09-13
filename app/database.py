from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Formato: postgresql://usuario:senha@localhost/nome_do_banco
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:8531@localhost/eventos_academicos"

# Cria o motor de conexão
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Cria a sessão para executar comandos no banco
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Classe base para criar as tabelas
Base = declarative_base()

# Função que a API usará para acessar o banco de dados
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()