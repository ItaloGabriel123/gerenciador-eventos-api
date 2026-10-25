from fastapi import APIRouter
from api.v1.endpoints import usuario, categoria, evento, inscricao, certificado, auth

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["Autenticação"])
api_router.include_router(usuario.router, prefix="/usuarios", tags=["Usuários"])
api_router.include_router(categoria.router, prefix="/categorias", tags=["Categorias"])
api_router.include_router(evento.router, prefix="/eventos", tags=["Eventos"])
api_router.include_router(inscricao.router, prefix="/inscricoes", tags=["Inscrições"])
api_router.include_router(certificado.router, prefix="/certificados", tags=["Certificados"])