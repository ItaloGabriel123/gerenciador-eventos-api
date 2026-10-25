from tests.conftest import get_auth_headers

def test_buscar_usuario_inexistente(client, admin_user):
    headers = get_auth_headers(admin_user.id)
    response = client.get("/api/v1/usuarios/99999", headers=headers)
    assert response.status_code == 404

def test_buscar_evento_inexistente(client):
    response = client.get("/api/v1/eventos/99999")
    assert response.status_code == 404