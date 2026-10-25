from tests.conftest import get_auth_headers

def test_criar_usuario_publico(client):
    payload = {
        "nome": "Novo Aluno",
        "email": "aluno@esuda.br",
        "senha": "senha_segura_123",
        "perfil": "PARTICIPANTE"
    }
    response = client.post("/api/v1/usuarios/", json=payload)
    assert response.status_code == 201
    assert response.json()["email"] == "aluno@esuda.br"

def test_admin_criar_categoria(client, admin_user):
    headers = get_auth_headers(admin_user.id)
    response = client.post("/api/v1/categorias/", json={"nome": "Tecnologia"}, headers=headers)
    assert response.status_code == 201
    assert response.json()["nome"] == "Tecnologia"

def test_consultar_usuario_logado(client, participante_user):
    headers = get_auth_headers(participante_user.id)
    response = client.get("/api/v1/usuarios/me", headers=headers)
    assert response.status_code == 200
    assert response.json()["email"] == "user@teste.com"

def test_deletar_categoria_admin(client, admin_user):
    headers = get_auth_headers(admin_user.id)
    cat_res = client.post("/api/v1/categorias/", json={"nome": "A Deletar"}, headers=headers)
    cat_id = cat_res.json()["id"]

    del_res = client.delete(f"/api/v1/categorias/{cat_id}", headers=headers)
    assert del_res.status_code == 204