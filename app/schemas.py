from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

# Categoria
class CategoriaBase(BaseModel):
    nome: str

class CategoriaCreate(CategoriaBase):
    pass

class CategoriaResponse(CategoriaBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

# Usuario
class UsuarioBase(BaseModel):
    nome: str
    email: str

class UsuarioCreate(UsuarioBase):
    senha: str

class UsuarioResponse(UsuarioBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

# Evento
class EventoBase(BaseModel):
    titulo: str
    descricao: Optional[str] = None
    data_evento: datetime
    capacidade: int
    organizador_id: int
    categoria_id: int

class EventoCreate(EventoBase):
    pass

class EventoResponse(EventoBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

# Inscricao
class InscricaoBase(BaseModel):
    evento_id: int
    usuario_id: int

class InscricaoCreate(InscricaoBase):
    pass

class InscricaoResponse(InscricaoBase):
    id: int
    status: str
    data_inscricao: datetime
    model_config = ConfigDict(from_attributes=True)

# Certificado
class CertificadoBase(BaseModel):
    inscricao_id: int

class CertificadoCreate(CertificadoBase):
    pass

class CertificadoResponse(CertificadoBase):
    id: int
    codigo_validacao: str
    data_emissao: datetime
    model_config = ConfigDict(from_attributes=True)