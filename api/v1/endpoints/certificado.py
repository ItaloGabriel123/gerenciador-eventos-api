import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from core.deps import get_db, get_usuario_logado, verificar_perfis
from models.inscricao_model import Inscricao
from models.certificado_model import Certificado
from models.usuario_model import Usuario
from schemas.certificado_schema import CertificadoCreate, CertificadoResponse

router = APIRouter()

@router.post("/", response_model=CertificadoResponse, status_code=status.HTTP_201_CREATED)
def emitir_certificado(
    certificado_data: CertificadoCreate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(verificar_perfis(["ADMINISTRADOR", "ORGANIZADOR"]))  # <-- Permitir ORGANIZADOR
):
    # Lógica de emissão do certificado...
    inscricao = db.query(Inscricao).filter(Inscricao.id == certificado.inscricao_id).first()
    if not inscricao:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inscrição não encontrada.")

    # Validation: O organizador só pode emitir certificado para o seu próprio evento
    if usuario_atual.perfil == "ORGANIZADOR" and inscricao.evento.organizador_id != usuario_atual.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permissão negada. Evento pertence a outro organizador.")

    certificado_existente = db.query(Certificado).filter(Certificado.inscricao_id == certificado.inscricao_id).first()
    if certificado_existente:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Certificado já emitido para esta inscrição.")

    codigo_unico = f"CERT-{uuid.uuid4().hex[:10].upper()}"

    db_certificado = Certificado(
        inscricao_id=certificado.inscricao_id,
        codigo_validacao=codigo_unico
    )
    db.add(db_certificado)
    db.commit()
    db.refresh(db_certificado)
    return db_certificado

@router.get("/", response_model=List[CertificadoResponse])
def listar_certificados(
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(get_usuario_logado)
):
    query = db.query(Certificado).join(Inscricao)
    if usuario_atual.perfil == "PARTICIPANTE":
        query = query.filter(Inscricao.usuario_id == usuario_atual.id)
    elif usuario_atual.perfil == "ORGANIZADOR":
        query = query.filter(Inscricao.evento.has(organizador_id=usuario_atual.id))
    return query.all()