from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from typing import Optional

class EventoBase(BaseModel):
    titulo: str
    descricao: Optional[str] = None
    data_inicio: datetime
    data_fim: Optional[datetime] = None
    capacidade: int = Field(gt=0, description="Capacidade deve ser maior que zero")
    organizador_id: Optional[int] = None
    categoria_id: Optional[int] = None

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