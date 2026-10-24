from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

class InscricaoBase(BaseModel):
    evento_id: int
    usuario_id: int

class InscricaoCreate(InscricaoBase):
    pass

class InscricaoUpdateStatus(BaseModel):
    status: str

class InscricaoResponse(InscricaoBase):
    id: int
    status: str
    data_inscricao: datetime
    
    model_config = ConfigDict(from_attributes=True)