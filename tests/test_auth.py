from tests.conftest import get_auth_headers

def test_login_sucesso(client, participante_user):
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "user@teste.com", "password": "senha123"}
    )
    assert response.status_code == 200
    json_data = response.json()
    assert "access_token" in json_data
    assert json_data["token_type"] == "bearer"

def test_login_senha_incorreta(client, participante_user):
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "user@teste.com", "password": "senha_errada"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "E-mail ou palavra-passe incorretos."

def test_rota_protegida_sem_token(client):
    response = client.get("/api/v1/usuarios/me")
    assert response.status_code == 401

def test_rota_protegida_token_invalido(client):
    response = client.get(
        "/api/v1/usuarios/me",
        headers={"Authorization": "Bearer token_completamente_invalido"}
    )
    assert response.status_code == 401