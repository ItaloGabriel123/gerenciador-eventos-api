from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from . import models, schemas
from .database import engine, get_db

app = FastAPI(title="API Eventos Acadêmicos", version="1.0")

@app.post("/api/v1/categorias", response_model=schemas.CategoriaResponse, status_code=201)
def criar_categoria(categoria: schemas.CategoriaCreate, db: Session = Depends(get_db)):
    db_categoria = models.Categoria(nome=categoria.nome)
    db.add(db_categoria)
    db.commit()
    db.refresh(db_categoria)
    return db_categoria

@app.get("/api/v1/categorias", response_model=list[schemas.CategoriaResponse])
def listar_categorias(db: Session = Depends(get_db)):
    return db.query(models.Categoria).all()

@app.post("/api/v1/usuarios", response_model=schemas.UsuarioResponse, status_code=201)
def criar_usuario(usuario: schemas.UsuarioCreate, db: Session = Depends(get_db)):
    # Em uma aplicação real, a senha receberia um hash (ex: bcrypt) antes de salvar
    db_usuario = models.Usuario(
        nome=usuario.nome,
        email=usuario.email,
        senha_hash=usuario.senha, 
        perfil=usuario.perfil
    )
    db.add(db_usuario)
    db.commit()
    db.refresh(db_usuario)
    return db_usuario

@app.get("/api/v1/usuarios", response_model=list[schemas.UsuarioResponse])
def listar_usuarios(db: Session = Depends(get_db)):
    return db.query(models.Usuario).all()

@app.post("/api/v1/eventos", response_model=schemas.EventoResponse, status_code=201)
def criar_evento(evento: schemas.EventoCreate, db: Session = Depends(get_db)):
    db_evento = models.Evento(
        titulo=evento.titulo,
        descricao=evento.descricao,
        data_evento=evento.data_evento,
        capacidade=evento.capacidade,
        organizador_id=evento.organizador_id,
        categoria_id=evento.categoria_id
    )
    db.add(db_evento)
    db.commit()
    db.refresh(db_evento)
    return db_evento

@app.post("/api/v1/inscricoes", response_model=schemas.InscricaoResponse, status_code=201)
def realizar_inscricao(inscricao: schemas.InscricaoCreate, db: Session = Depends(get_db)):
    db_inscricao = models.Inscricao(
        usuario_id=inscricao.usuario_id,
        evento_id=inscricao.evento_id
    )
    db.add(db_inscricao)
    db.commit()
    db.refresh(db_inscricao)
    return db_inscricao