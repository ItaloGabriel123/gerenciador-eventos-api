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