from tests.conftest import get_auth_headers

def test_participante_nao_pode_listar_todos_usuarios(client, participante_user):
    headers = get_auth_headers(participante_user.id)
    response = client.get("/api/v1/usuarios/", headers=headers)
    assert response.status_code == 403

def test_admin_pode_listar_usuarios(client, admin_user):
    headers = get_auth_headers(admin_user.id)
    response = client.get("/api/v1/usuarios/", headers=headers)
    assert response.status_code == 200

def test_participante_nao_pode_criar_categoria(client, participante_user):
    headers = get_auth_headers(participante_user.id)
    response = client.post(
        "/api/v1/categorias/",
        json={"nome": "Nova Categoria"},
        headers=headers
    )
    assert response.status_code == 403

def test_organizador_nao_pode_deletar_usuario(client, organizador_user, participante_user):
    headers = get_auth_headers(organizador_user.id)
    response = client.delete(f"/api/v1/usuarios/{participante_user.id}", headers=headers)
    assert response.status_code == 403