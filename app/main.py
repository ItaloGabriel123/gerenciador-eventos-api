import uuid
from typing import List, Optional
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app import models, schemas
from app.database import get_db

app = FastAPI(title="API Eventos Acadêmicos", version="1.0")


# --- CATEGORIAS ---
@app.post("/api/v1/categorias", response_model=schemas.CategoriaResponse, status_code=status.HTTP_201_CREATED)
def criar_categoria(categoria: schemas.CategoriaCreate, db: Session = Depends(get_db)):
    db_categoria = models.Categoria(nome=categoria.nome)
    db.add(db_categoria)
    db.commit()
    db.refresh(db_categoria)
    return db_categoria

@app.get("/api/v1/categorias", response_model=List[schemas.CategoriaResponse])
def listar_categorias(db: Session = Depends(get_db)):
    return db.query(models.Categoria).all()


# --- USUÁRIOS ---
@app.post("/api/v1/usuarios", response_model=schemas.UsuarioResponse, status_code=status.HTTP_201_CREATED)
def criar_usuario(usuario: schemas.UsuarioCreate, db: Session = Depends(get_db)):
    usuario_existente = db.query(models.Usuario).filter(models.Usuario.email == usuario.email).first()
    if usuario_existente:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="E-mail já cadastrado.")

    db_usuario = models.Usuario(
        nome=usuario.nome,
        email=usuario.email,
        senha=usuario.senha
    )
    db.add(db_usuario)
    db.commit()
    db.refresh(db_usuario)
    return db_usuario

@app.get("/api/v1/usuarios", response_model=List[schemas.UsuarioResponse])
def listar_usuarios(db: Session = Depends(get_db)):
    return db.query(models.Usuario).all()


# --- EVENTOS ---
@app.post("/api/v1/eventos", response_model=schemas.EventoResponse, status_code=status.HTTP_201_CREATED)
def criar_evento(evento: schemas.EventoCreate, db: Session = Depends(get_db)):
    categoria = db.query(models.Categoria).filter(models.Categoria.id == evento.categoria_id).first()
    if not categoria:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Categoria não encontrada.")

    organizador = db.query(models.Usuario).filter(models.Usuario.id == evento.organizador_id).first()
    if not organizador:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organizador não encontrado.")

    db_evento = models.Evento(**evento.model_dump())
    db.add(db_evento)
    db.commit()
    db.refresh(db_evento)
    return db_evento

@app.get("/api/v1/eventos", response_model=List[schemas.EventoResponse])
def listar_eventos(categoria_id: Optional[int] = None, db: Session = Depends(get_db)):
    query = db.query(models.Evento)
    if categoria_id:
        query = query.filter(models.Evento.categoria_id == categoria_id)
    return query.all()

@app.get("/api/v1/eventos/{evento_id}", response_model=schemas.EventoResponse)
def obter_evento(evento_id: int, db: Session = Depends(get_db)):
    evento = db.query(models.Evento).filter(models.Evento.id == evento_id).first()
    if not evento:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Evento não encontrado.")
    return evento


# --- INSCRIÇÕES ---
@app.post("/api/v1/inscricoes", response_model=schemas.InscricaoResponse, status_code=status.HTTP_201_CREATED)
def realizar_inscricao(inscricao: schemas.InscricaoCreate, db: Session = Depends(get_db)):
    # 1. Valida existência do Evento
    evento = db.query(models.Evento).filter(models.Evento.id == inscricao.evento_id).first()
    if not evento:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Evento não encontrado.")

    # 2. Valida existência do Usuário
    usuario = db.query(models.Usuario).filter(models.Usuario.id == inscricao.usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado.")

    # 3. Regra: Bloqueia inscrições duplicadas do mesmo usuário no mesmo evento
    inscricao_existente = db.query(models.Inscricao).filter(
        models.Inscricao.usuario_id == inscricao.usuario_id,
        models.Inscricao.evento_id == inscricao.evento_id
    ).first()
    if inscricao_existente:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Usuário já está inscrito neste evento.")

    # 4. Regra: Valida capacidade máxima do evento
    total_inscritos = db.query(models.Inscricao).filter(models.Inscricao.evento_id == inscricao.evento_id).count()
    if total_inscritos >= evento.capacidade:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Evento lotado. Capacidade máxima atingida.")

    db_inscricao = models.Inscricao(**inscricao.model_dump())
    db.add(db_inscricao)
    db.commit()
    db.refresh(db_inscricao)
    return db_inscricao


# --- CERTIFICADOS ---
@app.post("/api/v1/certificados", response_model=schemas.CertificadoResponse, status_code=status.HTTP_201_CREATED)
def emitir_certificado(certificado: schemas.CertificadoCreate, db: Session = Depends(get_db)):
    inscricao = db.query(models.Inscricao).filter(models.Inscricao.id == certificado.inscricao_id).first()
    if not inscricao:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inscrição não encontrada.")

    # Impedir emissão de mais de um certificado para a mesma inscrição
    certificado_existente = db.query(models.Certificado).filter(models.Certificado.inscricao_id == certificado.inscricao_id).first()
    if certificado_existente:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Certificado já emitido para esta inscrição.")

    # Gera código hash único de validação
    codigo_unico = f"CERT-{uuid.uuid4().hex[:10].upper()}"

    db_certificado = models.Certificado(
        inscricao_id=certificado.inscricao_id,
        codigo_validacao=codigo_unico
    )
    db.add(db_certificado)
    db.commit()
    db.refresh(db_certificado)
    return db_certificado