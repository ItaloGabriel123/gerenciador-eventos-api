from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from core.database import Base

class Certificado(Base):
    __tablename__ = "certificados"

    id = Column(Integer, primary_key=True, index=True)
    inscricao_id = Column(Integer, ForeignKey("inscricoes.id"), unique=True, nullable=False)
    codigo_validacao = Column(String(50), unique=True, nullable=False)
    data_emissao = Column(DateTime, default=datetime.utcnow)

    inscricao = relationship("Inscricao", back_populates="certificado")