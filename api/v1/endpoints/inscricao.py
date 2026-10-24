from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from core.deps import get_db
from models.evento_model import Evento
from models.usuario_model import Usuario
from models.inscricao_model import Inscricao
from schemas.inscricao_schema import InscricaoCreate, InscricaoResponse, InscricaoUpdateStatus

router = APIRouter(prefix="/inscricoes", tags=["Inscrições"])

@router.post("/", response_model=InscricaoResponse, status_code=status.HTTP_201_CREATED)
def realizar_inscricao(inscricao: InscricaoCreate, db: Session = Depends(get_db)):
    evento = db.query(Evento).filter(Evento.id == inscricao.evento_id).first()
    if not evento:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Evento não encontrado.")

    usuario = db.query(Usuario).filter(Usuario.id == inscricao.usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado.")

    inscricao_existente = db.query(Inscricao).filter(
        Inscricao.usuario_id == inscricao.usuario_id,
        Inscricao.evento_id == inscricao.evento_id
    ).first()
    if inscricao_existente:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Usuário já está inscrito neste evento.")

    total_inscritos = db.query(Inscricao).filter(Inscricao.evento_id == inscricao.evento_id).count()
    if total_inscritos >= evento.capacidade:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Evento lotado. Capacidade máxima atingida.")

    db_inscricao = Inscricao(**inscricao.model_dump())
    db.add(db_inscricao)
    db.commit()
    db.refresh(db_inscricao)
    return db_inscricao

@router.get("/", response_model=List[InscricaoResponse])
def listar_inscricoes(
    usuario_id: Optional[int] = None, 
    evento_id: Optional[int] = None, 
    db: Session = Depends(get_db)
):
    query = db.query(Inscricao)
    if usuario_id:
        query = query.filter(Inscricao.usuario_id == usuario_id)
    if evento_id:
        query = query.filter(Inscricao.evento_id == evento_id)
    return query.all()

@router.get("/{inscricao_id}", response_model=InscricaoResponse)
def obter_inscricao(inscricao_id: int, db: Session = Depends(get_db)):
    inscricao = db.query(Inscricao).filter(Inscricao.id == inscricao_id).first()
    if not inscricao:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inscrição não encontrada.")
    return inscricao

@router.patch("/{inscricao_id}/status", response_model=InscricaoResponse)
def alterar_status_inscricao(
    inscricao_id: int, 
    dados: InscricaoUpdateStatus, 
    db: Session = Depends(get_db)
):
    inscricao = db.query(Inscricao).filter(Inscricao.id == inscricao_id).first()
    if not inscricao:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inscrição não encontrada.")
    
    inscricao.status = dados.status.upper()
    db.commit()
    db.refresh(inscricao)
    return inscricao

@router.delete("/{inscricao_id}", status_code=status.HTTP_204_NO_CONTENT)
def cancelar_inscricao(inscricao_id: int, db: Session = Depends(get_db)):
    inscricao = db.query(Inscricao).filter(Inscricao.id == inscricao_id).first()
    if not inscricao:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inscrição não encontrada.")
    
    db.delete(inscricao)
    db.commit()
    return None