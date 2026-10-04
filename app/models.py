from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, index=True, nullable=False)
    senha_hash = Column(String(255), nullable=False)
    perfil = Column(String(20), nullable=False, default="PARTICIPANTE")

    # Relacionamentos
    eventos = relationship("Evento", back_populates="organizador")
    inscricoes = relationship("Inscricao", back_populates="usuario")


class Categoria(Base):
    __tablename__ = "categorias"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)

    # Relacionamentos
    eventos = relationship("Evento", back_populates="categoria")


class Evento(Base):
    __tablename__ = "eventos"

    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String(150), nullable=False)
    descricao = Column(String(500))
    data_inicio = Column(DateTime, nullable=False)
    data_fim = Column(DateTime, nullable=False)
    capacidade = Column(Integer)
    organizador_id = Column(Integer, ForeignKey("usuarios.id"))
    categoria_id = Column(Integer, ForeignKey("categorias.id"))

    # Relacionamentos
    organizador = relationship("Usuario", back_populates="eventos")
    categoria = relationship("Categoria", back_populates="eventos")
    inscricoes = relationship("Inscricao", back_populates="evento")


class Inscricao(Base):
    __tablename__ = "inscricoes"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    evento_id = Column(Integer, ForeignKey("eventos.id"), nullable=False)
    status = Column(String(20), nullable=False, default="CONFIRMADA")
    data_inscricao = Column(DateTime, default=datetime.utcnow)

    # Relacionamentos
    usuario = relationship("Usuario", back_populates="inscricoes")
    evento = relationship("Evento", back_populates="inscricoes")
    certificado = relationship("Certificado", back_populates="inscricao", uselist=False)


class Certificado(Base):
    __tablename__ = "certificados"

    id = Column(Integer, primary_key=True, index=True)
    inscricao_id = Column(Integer, ForeignKey("inscricoes.id"), unique=True, nullable=False)
    codigo_validacao = Column(String(50), unique=True, nullable=False)
    data_emissao = Column(DateTime, default=datetime.utcnow)

    # Relacionamentos
    inscricao = relationship("Inscricao", back_populates="certificado")