from pydantic import BaseModel
from datetime import datetime

class CategoriaBase(BaseModel):
    nome: str

class CategoriaCreate(CategoriaBase):
    pass

class CategoriaResponse(CategoriaBase):
    id: int

class Config:
        from_attributes = True

class UsuarioBase(BaseModel):
    nome: str
    email: str
    perfil: str

class UsuarioCreate(UsuarioBase):
    senha: str

class UsuarioResponse(UsuarioBase):
    id: int

    class Config:
        from_attributes = True

class EventoBase(BaseModel):
    titulo: str
    descricao: str | None = None
    data_evento: datetime
    capacidade: int
    organizador_id: int
    categoria_id: int

class EventoCreate(EventoBase):
    pass

class EventoResponse(EventoBase):
    id: int

    class Config:
        from_attributes = True

class InscricaoBase(BaseModel):
    evento_id: int
    usuario_id: int

class InscricaoCreate(InscricaoBase):
    pass

class InscricaoResponse(InscricaoBase):
    id: int
    status: str
    data_inscricao: datetime

    class Config:
        from_attributes = True