import streamlit as st
import requests
import streamlit.components.v1 as components
from datetime import datetime, time

# Endereço base da API FastAPI
API_URL = "http://localhost:8000/api/v1"

st.set_page_config(page_title="Gestão de Eventos Académicos", page_icon="🎓", layout="wide")

# <-- NOVO: impede o Chrome de traduzir a página automaticamente
components.html(
    """
    <script>
        const doc = window.parent.document;
        doc.documentElement.setAttribute('lang', 'pt');
        doc.documentElement.setAttribute('translate', 'no');
        doc.body.classList.add('notranslate');
    </script>
    """,
    height=0,
)

# Título Principal Global
st.title("🎓 Gestão de Eventos Académicos")

# Menu lateral para navegação
menu = st.sidebar.selectbox(
    "Navegação",
    ["Categorias", "Utilizadores", "Eventos", "Inscrições", "Certificados"]
)

# Funções auxiliares para evitar erros visuais se a API estiver offline
def safe_get(endpoint):
    try:
        res = requests.get(f"{API_URL}{endpoint}")
        if res.status_code == 200:
            return res.json()
    except requests.exceptions.RequestException:
        st.error("⚠️ Não foi possível conectar ao servidor backend (FastAPI na porta 8000).")
    return []

def safe_post(endpoint, payload):
    try:
        return requests.post(f"{API_URL}{endpoint}", json=payload)
    except requests.exceptions.RequestException:
        st.error("⚠️ Erro de conexão com a API.")
        return None

# ---------------------------------------------------------
# 1. CATEGORIAS
# ---------------------------------------------------------
if menu == "Categorias":
    st.header("🏷️ Gestão de Categorias")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Criar Categoria")
        nome_cat = st.text_input("Nome da Categoria")
        if st.button("Guardar Categoria"):
            if nome_cat:
                res = safe_post("/categorias/", {"nome": nome_cat})
                if res and res.status_code in [200, 201]:
                    st.success("Categoria criada com sucesso!")
                    st.rerun()
                elif res:
                    st.error(f"Erro ao criar: {res.json().get('detail')}")
            else:
                st.warning("Preencha o nome da categoria.")

    with col2:
        st.subheader("Categorias Existentes")
        categorias = safe_get("/categorias/")
        if categorias:
            st.dataframe(categorias, width='stretch') # Se aparecer erro ou aviso, troque por use_container_width=True

# ---------------------------------------------------------
# 2. UTILIZADORES
# ---------------------------------------------------------
elif menu == "Utilizadores":
    st.header("👤 Gestão de Utilizadores")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Novo Utilizador")
        nome_user = st.text_input("Nome Completo")
        email_user = st.text_input("E-mail")
        senha_user = st.text_input("Palavra-passe", type="password")
        perfil_user = st.selectbox("Perfil", ["PARTICIPANTE", "ORGANIZADOR"])
        
        if st.button("Cadastrar Utilizador"):
            if nome_user and email_user and senha_user:
                payload = {
                    "nome": nome_user,
                    "email": email_user,
                    "senha": senha_user,
                    "perfil": perfil_user
                }
                res = safe_post("/usuarios/", payload)
                if res and res.status_code in [200, 201]:
                    st.success("Utilizador registado com sucesso!")
                    st.rerun()
                elif res:
                    st.error(f"Erro: {res.json().get('detail')}")
            else:
                st.warning("Preencha todos os campos obrigatórios.")

    with col2:
        st.subheader("Utilizadores Registados")
        usuarios = safe_get("/usuarios/")
        if usuarios:
            st.dataframe(usuarios, width='stretch') # Se aparecer erro ou aviso, troque por use_container_width=True

# ---------------------------------------------------------
# 3. EVENTOS
# ---------------------------------------------------------
elif menu == "Eventos":
    st.header("📅 Gestão de Eventos")
    
    col1, col2 = st.columns(2)
    
    categorias = safe_get("/categorias/")
    usuarios = safe_get("/usuarios/")
    
    dict_cat = {c["nome"]: c["id"] for c in categorias if "nome" in c}
    dict_org = {f"{u['nome']} ({u['email']})": u["id"] for u in usuarios if "nome" in u}
    
    with col1:
        st.subheader("Criar Novo Evento")
        titulo = st.text_input("Título do Evento")
        descricao = st.text_area("Descrição")
        vagas = st.number_input("Limite de Vagas / Capacidade", min_value=1, value=50)
        
        col_d1, col_d2 = st.columns(2)
        with col_d1:
            d_inicio = st.date_input("Data de Início")
            t_inicio = st.time_input("Hora de Início", value=time(9, 0))
        with col_d2:
            d_fim = st.date_input("Data de Término")
            t_fim = st.time_input("Hora de Término", value=time(18, 0))
            
        cat_nome = st.selectbox("Categoria", list(dict_cat.keys())) if dict_cat else None
        org_nome = st.selectbox("Organizador", list(dict_org.keys())) if dict_org else None
        
        if st.button("Criar Evento"):
            if titulo and cat_nome and org_nome:
                dt_inicio = datetime.combine(d_inicio, t_inicio).isoformat()
                dt_fim = datetime.combine(d_fim, t_fim).isoformat()
                
                payload = {
                    "titulo": titulo,
                    "descricao": descricao,
                    "capacidade": vagas,
                    "data_inicio": dt_inicio,
                    "data_fim": dt_fim,
                    "categoria_id": dict_cat[cat_nome],
                    "organizador_id": dict_org[org_nome]
                }
                res = safe_post("/eventos/", payload)
                if res and res.status_code in [200, 201]:
                    st.success("Evento criado com sucesso!")
                    st.rerun()
                elif res:
                    st.error(f"Erro: {res.json().get('detail')}")
            else:
                st.warning("Preencha todos os campos e assegure-se de que existem categorias e utilizadores registados.")

    with col2:
        st.subheader("Lista de Eventos")
        eventos = safe_get("/eventos/")
        if eventos:
            st.dataframe(eventos, width='stretch') # Se aparecer erro ou aviso, troque por use_container_width=True

# ---------------------------------------------------------
# 4. INSCRIÇÕES
# ---------------------------------------------------------
elif menu == "Inscrições":
    st.header("✍️ Gestão de Inscrições")
    
    col1, col2 = st.columns(2)
    
    usuarios = safe_get("/usuarios/")
    eventos = safe_get("/eventos/")
    
    dict_users = {f"{u['nome']} ({u['email']})": u["id"] for u in usuarios if "nome" in u}
    dict_eventos = {f"{e['titulo']} (ID: {e['id']})": e["id"] for e in eventos if "titulo" in e}
    
    with col1:
        st.subheader("Realizar Inscrição")
        user_sel = st.selectbox("Utilizador", list(dict_users.keys())) if dict_users else None
        ev_sel = st.selectbox("Evento", list(dict_eventos.keys())) if dict_eventos else None
        
        if st.button("Inscrever"):
            if user_sel and ev_sel:
                payload = {
                    "usuario_id": dict_users[user_sel],
                    "evento_id": dict_eventos[ev_sel]
                }
                res = safe_post("/inscricoes/", payload)
                if res and res.status_code in [200, 201]:
                    st.success(f"Inscrição realizada com sucesso! ID da Inscrição: {res.json().get('id')}")
                    st.rerun()
                elif res:
                    st.error(f"Erro ao inscrever: {res.json().get('detail')}")

    with col2:
        st.subheader("Inscrições Realizadas")
        inscricoes = safe_get("/inscricoes/")
        if inscricoes:
            st.dataframe(inscricoes, width='stretch') # Se aparecer erro ou aviso, troque por use_container_width=True

# ---------------------------------------------------------
# 5. CERTIFICADOS
# ---------------------------------------------------------
elif menu == "Certificados":
    st.header("📜 Emissão de Certificados")
    
    st.subheader("Emitir Certificado por Inscrição")
    
    inscricoes = safe_get("/inscricoes/")
    dict_insc = {f"Inscrição #{i['id']} (Utilizador ID: {i['usuario_id']} | Evento ID: {i['evento_id']})": i["id"] for i in inscricoes if "id" in i}
    
    if dict_insc:
        insc_sel = st.selectbox("Selecione a Inscrição", list(dict_insc.keys()))
        inscricao_id = dict_insc[insc_sel]
    else:
        inscricao_id = st.number_input("ID da Inscrição", min_value=1, step=1)
    
    if st.button("Emitir Certificado"):
        payload = {"inscricao_id": inscricao_id}
        res = safe_post("/certificados/", payload)
        
        if res and res.status_code in [200, 201]:
            cert = res.json()
            st.success("🎉 Certificado emitido com sucesso! O e-mail foi agendado em segundo plano.")
            st.json(cert)
        elif res:
            st.error(f"Erro ao emitir certificado: {res.json().get('detail')}")