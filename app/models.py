from sqlalchemy import Column, Integer, String
from .database import Base

class Categoria(Base):
    __tablename__ = "categorias"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(50), unique=True, index=True, nullable=False)