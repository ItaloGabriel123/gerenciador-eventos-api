from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from core.deps import get_db, get_usuario_logado
from models.evento_model import Evento
from models.usuario_model import Usuario
from models.inscricao_model import Inscricao
from schemas.inscricao_schema import InscricaoCreate, InscricaoResponse, InscricaoUpdateStatus

# Correção: O prefixo "/inscricoes" já é definido na inclusão do router em api.py
router = APIRouter()

@router.post("/", response_model=InscricaoResponse, status_code=status.HTTP_201_CREATED)
def realizar_inscricao(
    inscricao: InscricaoCreate, 
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(get_usuario_logado)
):
    # Regra de Segurança: O participante apenas pode inscrever a si próprio.
    # O ADMINISTRADOR pode inscrever qualquer utilizador.
    target_usuario_id = usuario_atual.id if usuario_atual.perfil != "ADMINISTRADOR" else inscricao.usuario_id

    evento = db.query(Evento).filter(Evento.id == inscricao.evento_id).first()
    if not evento:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Evento não encontrado.")

    target_user = db.query(Usuario).filter(Usuario.id == target_usuario_id).first()
    if not target_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado.")

    # Regra de Negócio: Impedir inscrição duplicada
    inscricao_existente = db.query(Inscricao).filter(
        Inscricao.usuario_id == target_usuario_id,
        Inscricao.evento_id == inscricao.evento_id
    ).first()
    if inscricao_existente:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Usuário já está inscrito neste evento.")

    # Regra de Negócio: Respeitar a capacidade máxima do evento
    total_inscritos = db.query(Inscricao).filter(Inscricao.evento_id == inscricao.evento_id).count()
    if total_inscritos >= evento.capacidade:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Evento lotado. Capacidade máxima atingida.")

    db_inscricao = Inscricao(
        usuario_id=target_usuario_id,
        evento_id=inscricao.evento_id,
        status="CONFIRMADA"
    )
    db.add(db_inscricao)
    db.commit()
    db.refresh(db_inscricao)
    return db_inscricao

@router.get("/", response_model=List[InscricaoResponse])
def listar_inscricoes(
    usuario_id: Optional[int] = None, 
    evento_id: Optional[int] = None, 
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(get_usuario_logado)
):
    query = db.query(Inscricao)

    # Matriz de Acesso RBAC:
    # PARTICIPANTE vê apenas as suas próprias inscrições.
    # ORGANIZADOR vê as inscrições dos eventos que organiza.
    # ADMINISTRADOR visualiza todas.
    if usuario_atual.perfil == "PARTICIPANTE":
        query = query.filter(Inscricao.usuario_id == usuario_atual.id)
    elif usuario_atual.perfil == "ORGANIZADOR":
        query = query.join(Evento).filter(Evento.organizador_id == usuario_atual.id)
    elif usuario_id and usuario_atual.perfil == "ADMINISTRADOR":
        query = query.filter(Inscricao.usuario_id == usuario_id)

    if evento_id:
        query = query.filter(Inscricao.evento_id == evento_id)

    return query.all()

@router.get("/{inscricao_id}", response_model=InscricaoResponse)
def obter_inscricao(
    inscricao_id: int, 
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(get_usuario_logado)
):
    inscricao = db.query(Inscricao).filter(Inscricao.id == inscricao_id).first()
    if not inscricao:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inscrição não encontrada.")

    # Ownership validation
    if usuario_atual.perfil == "PARTICIPANTE" and inscricao.usuario_id != usuario_atual.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso negado.")

    return inscricao

@router.delete("/{inscricao_id}", status_code=status.HTTP_204_NO_CONTENT)
def cancelar_inscricao(
    inscricao_id: int, 
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(get_usuario_logado)
):
    inscricao = db.query(Inscricao).filter(Inscricao.id == inscricao_id).first()
    if not inscricao:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inscrição não encontrada.")

    if usuario_atual.perfil != "ADMINISTRADOR" and inscricao.usuario_id != usuario_atual.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso negado.")

    db.delete(inscricao)
    db.commit()
    return None