from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_criar_categoria():
    response = client.post("/api/v1/categorias", json={"nome": "Workshop"})
    assert response.status_code in [200, 201]

def test_bloqueio_inscricao_duplicada():
    payload = {"usuario_id": 1, "evento_id": 1}
    # Tenta inscrever novamente um usuário que já está inscrito
    response = client.post("/api/v1/inscricoes", json=payload)
    assert response.status_code == 400
    assert response.json()["detail"] == "Usuário já está inscrito neste evento."

def test_bloqueio_certificado_duplicado():
    payload = {"inscricao_id": 1}
    # Tenta emitir certificado novamente para uma inscrição que já possui certificado
    response = client.post("/api/v1/certificados", json=payload)
    assert response.status_code == 400
    assert response.json()["detail"] == "Certificado já emitido para esta inscrição."