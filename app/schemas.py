from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from typing import Optional

# --- CATEGORIAS ---
class CategoriaBase(BaseModel):
    nome: str

class CategoriaCreate(CategoriaBase):
    pass

class CategoriaUpdate(BaseModel):
    nome: Optional[str] = None

class CategoriaResponse(CategoriaBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


# --- USUÁRIOS ---
class UsuarioBase(BaseModel):
    nome: str
    email: str
    perfil: Optional[str] = "PARTICIPANTE"

class UsuarioCreate(UsuarioBase):
    senha: str

class UsuarioUpdate(BaseModel):
    nome: Optional[str] = None
    email: Optional[str] = None
    senha: Optional[str] = None
    perfil: Optional[str] = None

class UsuarioResponse(UsuarioBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


# --- EVENTOS ---
class EventoBase(BaseModel):
    titulo: str
    descricao: Optional[str] = None
    data_inicio: datetime
    data_fim: datetime
    capacidade: int = Field(gt=0, description="Capacidade deve ser maior que zero")
    organizador_id: int
    categoria_id: int

class EventoCreate(EventoBase):
    pass

class EventoUpdate(BaseModel):
    titulo: Optional[str] = None
    descricao: Optional[str] = None
    data_inicio: Optional[datetime] = None
    data_fim: Optional[datetime] = None
    capacidade: Optional[int] = Field(default=None, gt=0)
    organizador_id: Optional[int] = None
    categoria_id: Optional[int] = None

class EventoResponse(EventoBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


# --- INSCRIÇÕES ---
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


# --- CERTIFICADOS ---
class CertificadoBase(BaseModel):
    inscricao_id: int

class CertificadoCreate(CertificadoBase):
    pass

class CertificadoResponse(CertificadoBase):
    id: int
    codigo_validacao: str
    data_emissao: datetime
    model_config = ConfigDict(from_attributes=True)