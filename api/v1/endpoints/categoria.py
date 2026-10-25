from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from core.deps import get_db, get_usuario_logado, verificar_perfis
from models.categoria_model import Categoria
from models.usuario_model import Usuario
from schemas.categoria_schema import CategoriaCreate, CategoriaResponse, CategoriaUpdate

router = APIRouter()

@router.post("/", response_model=CategoriaResponse, status_code=status.HTTP_201_CREATED)
def criar_categoria(
    categoria: CategoriaCreate, 
    db: Session = Depends(get_db),
    _: Usuario = Depends(verificar_perfis(["ADMINISTRADOR"]))
):
    cat_existente = db.query(Categoria).filter(Categoria.nome == categoria.nome).first()
    if cat_existente:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Categoria já existente.")
    
    db_cat = Categoria(nome=categoria.nome)
    db.add(db_cat)
    db.commit()
    db.refresh(db_cat)
    return db_cat

@router.get("/", response_model=List[CategoriaResponse])
def listar_categorias(db: Session = Depends(get_db)):
    return db.query(Categoria).all()

@router.get("/{categoria_id}", response_model=CategoriaResponse)
def obter_categoria(categoria_id: int, db: Session = Depends(get_db)):
    cat = db.query(Categoria).filter(Categoria.id == categoria_id).first()
    if not cat:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Categoria não encontrada.")
    return cat

@router.put("/{categoria_id}", response_model=CategoriaResponse)
def atualizar_categoria(
    categoria_id: int, 
    cat_data: CategoriaUpdate, 
    db: Session = Depends(get_db),
    _: Usuario = Depends(verificar_perfis(["ADMINISTRADOR"]))
):
    db_cat = db.query(Categoria).filter(Categoria.id == categoria_id).first()
    if not db_cat:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Categoria não encontrada.")
    if cat_data.nome:
        db_cat.nome = cat_data.nome
    db.commit()
    db.refresh(db_cat)
    return db_cat

@router.delete("/{categoria_id}", status_code=status.HTTP_204_NO_CONTENT)
def deletar_categoria(
    categoria_id: int, 
    db: Session = Depends(get_db),
    _: Usuario = Depends(verificar_perfis(["ADMINISTRADOR"]))
):
    db_cat = db.query(Categoria).filter(Categoria.id == categoria_id).first()
    if not db_cat:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Categoria não encontrada.")
    db.delete(db_cat)
    db.commit()
    return None