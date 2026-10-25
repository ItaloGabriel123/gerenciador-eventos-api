from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from core.deps import get_db, get_usuario_logado, verificar_perfis
from models.evento_model import Evento
from models.categoria_model import Categoria
from models.usuario_model import Usuario
from schemas.evento_schema import EventoCreate, EventoResponse, EventoUpdate

router = APIRouter()

@router.post("/", response_model=EventoResponse, status_code=status.HTTP_201_CREATED)
def criar_evento(
    evento: EventoCreate, 
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(verificar_perfis(["ADMINISTRADOR", "ORGANIZADOR"]))
):
    data_inicio_naive = evento.data_inicio.replace(tzinfo=None) if evento.data_inicio.tzinfo else evento.data_inicio
    data_fim_naive = evento.data_fim.replace(tzinfo=None) if evento.data_fim.tzinfo else evento.data_fim

    if data_inicio_naive < datetime.utcnow():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Não é permitido cadastrar evento com data de início no passado.")

    if data_fim_naive <= data_inicio_naive:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="A data de término deve ser posterior à data de início.")

    categoria = db.query(Categoria).filter(Categoria.id == evento.categoria_id).first()
    if not categoria:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Categoria não encontrada.")

    # Se for ORGANIZADOR, vincula automaticamente ao próprio utilizador logado
    organizador_id = usuario_atual.id if usuario_atual.perfil == "ORGANIZADOR" else evento.organizador_id
    
    organizador = db.query(Usuario).filter(Usuario.id == organizador_id).first()
    if not organizador:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organizador não encontrado.")

    db_evento = Evento(
        titulo=evento.titulo,
        descricao=evento.descricao,
        capacidade=evento.capacidade,
        data_inicio=data_inicio_naive,
        data_fim=data_fim_naive,
        categoria_id=evento.categoria_id,
        organizador_id=organizador_id
    )
    db.add(db_evento)
    db.commit()
    db.refresh(db_evento)
    return db_evento

@router.get("/", response_model=List[EventoResponse])
def listar_eventos(categoria_id: Optional[int] = None, db: Session = Depends(get_db)):
    query = db.query(Evento)
    if categoria_id:
        query = query.filter(Evento.categoria_id == categoria_id)
    return query.all()

@router.get("/{evento_id}", response_model=EventoResponse)
def obter_evento(evento_id: int, db: Session = Depends(get_db)):
    evento = db.query(Evento).filter(Evento.id == evento_id).first()
    if not evento:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Evento não encontrado.")
    return evento

@router.put("/{evento_id}", response_model=EventoResponse)
def atualizar_evento(
    evento_id: int, 
    evento_data: EventoUpdate, 
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(verificar_perfis(["ADMINISTRADOR", "ORGANIZADOR"]))
):
    db_evento = db.query(Evento).filter(Evento.id == evento_id).first()
    if not db_evento:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Evento não encontrado.")

    # Resource Ownership: Organizador só pode alterar o seu próprio evento
    if usuario_atual.perfil == "ORGANIZADOR" and db_evento.organizador_id != usuario_atual.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permissão negada para alterar eventos de outros organizadores.")

    update_data = evento_data.model_dump(exclude_unset=True)

    nova_inicio = update_data.get("data_inicio", db_evento.data_inicio)
    nova_fim = update_data.get("data_fim", db_evento.data_fim)

    if "data_inicio" in update_data or "data_fim" in update_data:
        inicio_naive = nova_inicio.replace(tzinfo=None) if nova_inicio.tzinfo else nova_inicio
        fim_naive = nova_fim.replace(tzinfo=None) if nova_fim.tzinfo else nova_fim

        if inicio_naive < datetime.utcnow():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Não é permitido alterar a data de início para o passado.")
        if fim_naive <= inicio_naive:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="A data de término deve ser posterior à data de início.")

    for field, value in update_data.items():
        setattr(db_evento, field, value)

    db.commit()
    db.refresh(db_evento)
    return db_evento

@router.delete("/{evento_id}", status_code=status.HTTP_204_NO_CONTENT)
def deletar_evento(
    evento_id: int, 
    db: Session = Depends(get_db),
    _: Usuario = Depends(verificar_perfis(["ADMINISTRADOR"]))
):
    db_evento = db.query(Evento).filter(Evento.id == evento_id).first()
    if not db_evento:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Evento não encontrado.")

    db.delete(db_evento)
    db.commit()
    return None