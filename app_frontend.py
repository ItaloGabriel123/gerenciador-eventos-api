import streamlit as st
import requests

# Endereço base da sua API FastAPI
API_URL = "http://localhost:8000/api/v1"

st.set_page_config(page_title="Gestão de Eventos Académicos", page_icon="🎓", layout="wide")

st.title("🎓 Gestão de Eventos Académicos")

# Menu lateral para navegação
menu = st.sidebar.selectbox(
    "Navegação",
    ["Categorias", "Utilizadores", "Eventos", "Inscrições", "Certificados"]
)

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
                res = requests.post(f"{API_URL}/categorias", json={"nome": nome_cat})
                if res.status_code in [200, 201]:
                    st.success("Categoria criada com sucesso!")
                else:
                    st.error(f"Erro ao criar: {res.json().get('detail')}")
            else:
                st.warning("Preencha o nome da categoria.")

    with col2:
        st.subheader("Categorias Existentes")
        res = requests.get(f"{API_URL}/categorias")
        if res.status_code == 200:
            categorias = res.json()
            st.dataframe(categorias, use_container_width=True)

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
        
        if st.button("Cadastrar Utilizador"):
            if nome_user and email_user and senha_user:
                payload = {"nome": nome_user, "email": email_user, "senha": senha_user}
                res = requests.post(f"{API_URL}/usuarios", json=payload)
                if res.status_code in [200, 201]:
                    st.success("Utilizador registado com sucesso!")
                else:
                    st.error(f"Erro: {res.json().get('detail')}")
            else:
                st.warning("Preencha todos os campos.")

    with col2:
        st.subheader("Utilizadores Registados")
        res = requests.get(f"{API_URL}/usuarios")
        if res.status_code == 200:
            st.dataframe(res.json(), use_container_width=True)

# ---------------------------------------------------------
# 3. EVENTOS
# ---------------------------------------------------------
elif menu == "Eventos":
    st.header("📅 Gestão de Eventos")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Criar Novo Evento")
        titulo = st.text_input("Título do Evento")
        descricao = st.text_area("Descrição")
        vagas = st.number_input("Limite de Vagas / Capacidade", min_value=1, value=50)
        
        cat_id = st.number_input("ID da Categoria", min_value=1, step=1)
        org_id = st.number_input("ID do Organizador (Utilizador)", min_value=1, step=1)
        
        if st.button("Criar Evento"):
            payload = {
                "titulo": titulo,
                "descricao": descricao,
                "capacidade_maxima": vagas,
                "categoria_id": cat_id,
                "organizador_id": org_id
            }
            res = requests.post(f"{API_URL}/eventos", json=payload)
            if res.status_code in [200, 201]:
                st.success("Evento criado com sucesso!")
            else:
                st.error(f"Erro: {res.json().get('detail')}")

    with col2:
        st.subheader("Lista de Eventos")
        res = requests.get(f"{API_URL}/eventos")
        if res.status_code == 200:
            st.dataframe(res.json(), use_container_width=True)

# ---------------------------------------------------------
# 4. INSCRIÇÕES
# ---------------------------------------------------------
elif menu == "Inscrições":
    st.header("✍️ Inscrições em Eventos")
    
    st.subheader("Realizar Inscrição")
    user_id = st.number_input("ID do Utilizador", min_value=1, step=1)
    evento_id = st.number_input("ID do Evento", min_value=1, step=1)
    
    if st.button("Inscrever"):
        payload = {"usuario_id": user_id, "evento_id": evento_id}
        res = requests.post(f"{API_URL}/inscricoes", json=payload)
        
        if res.status_code in [200, 201]:
            st.success(f"Inscrição realizada com sucesso! ID da Inscrição: {res.json().get('id')}")
        else:
            st.error(f"Erro ao inscrever: {res.json().get('detail')}")

# ---------------------------------------------------------
# 5. CERTIFICADOS
# ---------------------------------------------------------
elif menu == "Certificados":
    st.header("📜 Emissão de Certificados")
    
    st.subheader("Emitir Certificado por Inscrição")
    inscricao_id = st.number_input("ID da Inscrição", min_value=1, step=1)
    
    if st.button("Emitir Certificado"):
        payload = {"inscricao_id": inscricao_id}
        res = requests.post(f"{API_URL}/certificados", json=payload)
        
        if res.status_code in [200, 201]:
            cert = res.json()
            st.success("🎉 Certificado emitido com sucesso!")
            st.json(cert)
        else:
            st.error(f"Erro ao emitir certificado: {res.json().get('detail')}")