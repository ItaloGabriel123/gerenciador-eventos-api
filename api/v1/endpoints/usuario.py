from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from core.deps import get_db, get_usuario_logado, verificar_perfis
from core.security import gerar_hash_senha
from models.usuario_model import Usuario
from schemas.usuario_schema import UsuarioCreate, UsuarioResponse, UsuarioUpdate

router = APIRouter()

@router.post("/", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED)
def criar_usuario(usuario: UsuarioCreate, db: Session = Depends(get_db)):
    usuario_existente = db.query(Usuario).filter(Usuario.email == usuario.email).first()
    if usuario_existente:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="E-mail já cadastrado.")

    # Segurança: Impede autorregisto direto como ADMINISTRADOR no cadastro público
    perfil_definido = usuario.perfil.upper() if usuario.perfil else "PARTICIPANTE"
    if perfil_definido == "ADMINISTRADOR":
        perfil_definido = "PARTICIPANTE"

    db_usuario = Usuario(
        nome=usuario.nome,
        email=usuario.email,
        senha_hash=gerar_hash_senha(usuario.senha),
        perfil=perfil_definido
    )
    db.add(db_usuario)
    db.commit()
    db.refresh(db_usuario)
    return db_usuario

@router.get("/me", response_model=UsuarioResponse)
def obter_usuario_logado(usuario_atual: Usuario = Depends(get_usuario_logado)):
    return usuario_atual

@router.get("/", response_model=List[UsuarioResponse])
def listar_usuarios(
    db: Session = Depends(get_db),
    _: Usuario = Depends(verificar_perfis(["ADMINISTRADOR", "ORGANIZADOR"]))  # <-- Permitir ORGANIZADOR
):
    return db.query(Usuario).all()

@router.get("/{usuario_id}", response_model=UsuarioResponse)
def obter_usuario(
    usuario_id: int, 
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(get_usuario_logado)
):
    if usuario_atual.perfil != "ADMINISTRADOR" and usuario_atual.id != usuario_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso negado.")
        
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado.")
    return usuario

@router.put("/{usuario_id}", response_model=UsuarioResponse)
def atualizar_usuario(
    usuario_id: int, 
    usuario_data: UsuarioUpdate, 
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(get_usuario_logado)
):
    # Apenas o próprio utilizador ou um ADMINISTRADOR pode alterar os dados
    if usuario_atual.perfil != "ADMINISTRADOR" and usuario_atual.id != usuario_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso negado.")

    db_usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not db_usuario:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado.")

    if usuario_data.email is not None and usuario_data.email != db_usuario.email:
        email_em_uso = db.query(Usuario).filter(Usuario.email == usuario_data.email).first()
        if email_em_uso:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="E-mail já cadastrado por outro usuário.")
        db_usuario.email = usuario_data.email

    if usuario_data.nome is not None:
        db_usuario.nome = usuario_data.nome
    if usuario_data.senha is not None:
        db_usuario.senha_hash = gerar_hash_senha(usuario_data.senha)
        
    # Impedir que utilizadores comuns alterem o próprio perfil para ADMINISTRADOR
    if usuario_data.perfil is not None:
        if usuario_atual.perfil == "ADMINISTRADOR":
            db_usuario.perfil = usuario_data.perfil

    db.commit()
    db.refresh(db_usuario)
    return db_usuario

@router.delete("/{usuario_id}", status_code=status.HTTP_204_NO_CONTENT)
def deletar_usuario(
    usuario_id: int, 
    db: Session = Depends(get_db),
    _: Usuario = Depends(verificar_perfis(["ADMINISTRADOR"]))
):
    db_usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not db_usuario:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado.")

    db.delete(db_usuario)
    db.commit()
    return None