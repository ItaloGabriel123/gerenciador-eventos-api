# API de Eventos Acadêmicos

API RESTful desenvolvida com **FastAPI** e **SQLAlchemy** para gestão de eventos, inscrições e emissão de certificados.

## Tecnologias
- Python 3.10+
- FastAPI
- SQLAlchemy
- Pydantic v2
- Pytest & HTTPX

## Funcionalidades
1. **Categorias e Usuários**: Cadastro com validação de e-mail único e ocultação de senha na resposta.
2. **Eventos**: Cadastro com limite de capacidade e vinculação a organizador e categoria.
3. **Inscrições**: Impedimento de inscrições duplicadas para o mesmo evento.
4. **Certificados**: Geração de código único de validação e bloqueio de emissão duplicada.

## Como Rodar a Aplicação
```bash
# Instalar dependências
pip install -r requirements.txt

# Iniciar o servidor
uvicorn app.main:app --reload

Sempre que for rodar o projeto no seu computador (ambiente local), você precisará manter dois terminais abertos simultaneamente:

Terminal 1 (Backend - FastAPI):
uvicorn app.main:app --reload
(Sobe o servidor da API em http://localhost:8000)

Terminal 2 (Frontend - Streamlit):
streamlit run app_frontend.py
(Sobe a interface visual em http://localhost:8501)