import os
import sys

# Adiciona a pasta raiz do projeto ao caminho de importação do Python
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from main import app
from core.database import Base
from core.deps import get_db
from core.security import gerar_hash_senha, criar_token_acesso
from models.usuario_model import Usuario

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db():
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            pass
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()

@pytest.fixture
def admin_user(db):
    user = Usuario(
        nome="Admin Teste",
        email="admin@teste.com",
        senha_hash=gerar_hash_senha("senha123"),
        perfil="ADMINISTRADOR"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@pytest.fixture
def organizador_user(db):
    user = Usuario(
        nome="Organizador Teste",
        email="org@teste.com",
        senha_hash=gerar_hash_senha("senha123"),
        perfil="ORGANIZADOR"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@pytest.fixture
def participante_user(db):
    user = Usuario(
        nome="Participante Teste",
        email="user@teste.com",
        senha_hash=gerar_hash_senha("senha123"),
        perfil="PARTICIPANTE"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def get_auth_headers(user_id: int) -> dict:
    token = criar_token_acesso(subject=user_id)
    return {"Authorization": f"Bearer {token}"}