from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from . import models, schemas
from .database import engine, get_db

# Cria a tabela no banco automaticamente para o MVP
models.Base.metadata.create_all(bind=engine)

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