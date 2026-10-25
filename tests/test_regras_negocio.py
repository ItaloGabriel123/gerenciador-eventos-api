from datetime import datetime, timedelta
from tests.conftest import get_auth_headers

def test_impedir_email_duplicado(client, participante_user):
    payload = {
        "nome": "Outro Usuario",
        "email": "user@teste.com",
        "senha": "123"
    }
    response = client.post("/api/v1/usuarios/", json=payload)
    assert response.status_code == 400
    assert response.json()["detail"] == "E-mail já cadastrado."

def test_impedir_categoria_duplicada(client, admin_user):
    headers = get_auth_headers(admin_user.id)
    client.post("/api/v1/categorias/", json={"nome": "I.A."}, headers=headers)
    response = client.post("/api/v1/categorias/", json={"nome": "I.A."}, headers=headers)
    assert response.status_code == 400

def test_impedir_inscricao_duplicada(client, admin_user, participante_user):
    headers = get_auth_headers(admin_user.id)
    cat_id = client.post("/api/v1/categorias/", json={"nome": "Dev"}, headers=headers).json()["id"]
    
    dt_inicio = (datetime.utcnow() + timedelta(days=1)).isoformat()
    dt_fim = (datetime.utcnow() + timedelta(days=2)).isoformat()
    
    ev_payload = {
        "titulo": "Workshop Python",
        "descricao": "Aula prática",
        "capacidade": 10,
        "data_inicio": dt_inicio,
        "data_fim": dt_fim,
        "categoria_id": cat_id,
        "organizador_id": admin_user.id
    }
    ev_id = client.post("/api/v1/eventos/", json=ev_payload, headers=headers).json()["id"]

    part_headers = get_auth_headers(participante_user.id)
    # Primeira inscrição
    client.post("/api/v1/inscricoes/", json={"evento_id": ev_id, "usuario_id": participante_user.id}, headers=part_headers)

    # Segunda inscrição (duplicada)
    res_dup = client.post("/api/v1/inscricoes/", json={"evento_id": ev_id, "usuario_id": participante_user.id}, headers=part_headers)
    assert res_dup.status_code == 400
    assert "já está inscrito" in res_dup.json()["detail"]

def test_respeitar_capacidade_maxima_evento(client, admin_user, participante_user):
    headers = get_auth_headers(admin_user.id)
    cat_id = client.post("/api/v1/categorias/", json={"nome": "Exclusivo"}, headers=headers).json()["id"]
    
    dt_inicio = (datetime.utcnow() + timedelta(days=1)).isoformat()
    dt_fim = (datetime.utcnow() + timedelta(days=2)).isoformat()

    ev_payload = {
        "titulo": "Palestra VIP",
        "descricao": "Vagas restritas",
        "capacidade": 1,
        "data_inicio": dt_inicio,
        "data_fim": dt_fim,
        "categoria_id": cat_id,
        "organizador_id": admin_user.id
    }
    ev_id = client.post("/api/v1/eventos/", json=ev_payload, headers=headers).json()["id"]

    part_headers = get_auth_headers(participante_user.id)
    client.post("/api/v1/inscricoes/", json={"evento_id": ev_id, "usuario_id": participante_user.id}, headers=part_headers)

    # Inscrição extra excedendo capacidade
    res_lotado = client.post("/api/v1/inscricoes/", json={"evento_id": ev_id, "usuario_id": admin_user.id}, headers=headers)
    assert res_lotado.status_code == 400
    assert "Evento lotado" in res_lotado.json()["detail"]

def test_impedir_autorregistro_como_admin(client):
    payload = {
        "nome": "Hacker Tentativa",
        "email": "hacker@teste.com",
        "senha": "123",
        "perfil": "ADMINISTRADOR"
    }
    res = client.post("/api/v1/usuarios/", json=payload)
    assert res.status_code == 201
    assert res.json()["perfil"] == "PARTICIPANTE"

def test_impedir_evento_com_data_no_passado(client, admin_user):
    headers = get_auth_headers(admin_user.id)
    cat_id = client.post("/api/v1/categorias/", json={"nome": "História"}, headers=headers).json()["id"]
    
    dt_passado = (datetime.utcnow() - timedelta(days=2)).isoformat()
    dt_fim = (datetime.utcnow() + timedelta(days=1)).isoformat()

    ev_payload = {
        "titulo": "Evento Passado",
        "descricao": "Inválido",
        "capacidade": 50,
        "data_inicio": dt_passado,
        "data_fim": dt_fim,
        "categoria_id": cat_id,
        "organizador_id": admin_user.id
    }
    res = client.post("/api/v1/eventos/", json=ev_payload, headers=headers)
    assert res.status_code == 400
    assert "no passado" in res.json()["detail"]