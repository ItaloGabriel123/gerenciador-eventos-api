from pydantic import BaseModel, ConfigDict
from datetime import datetime

class CertificadoBase(BaseModel):
    inscricao_id: int

class CertificadoCreate(CertificadoBase):
    pass

class CertificadoResponse(CertificadoBase):
    id: int
    codigo_validacao: str
    data_emissao: datetime
    model_config = ConfigDict(from_attributes=True)