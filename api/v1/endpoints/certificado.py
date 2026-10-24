import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from core.deps import get_db
from models.inscricao_model import Inscricao
from models.certificado_model import Certificado
from schemas.certificado_schema import CertificadoCreate, CertificadoResponse

router = APIRouter()

@router.post("/", response_model=CertificadoResponse, status_code=status.HTTP_201_CREATED)
def emitir_certificado(certificado: CertificadoCreate, db: Session = Depends(get_db)):
    inscricao = db.query(Inscricao).filter(Inscricao.id == certificado.inscricao_id).first()
    if not inscricao:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inscrição não encontrada.")

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