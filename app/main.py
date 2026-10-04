import uuid
from datetime import datetime
from typing import List, Optional
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app import models, schemas
from app.database import get_db

app = FastAPI(title="API Eventos Acadêmicos", version="1.0")


# ==========================================
# 1. ENTIDADE CATEGORIAS (CRUD Completo)
# ==========================================

# CREATE (POST)
@app.post("/api/v1/categorias", response_model=schemas.CategoriaResponse, status_code=status.HTTP_201_CREATED)
def criar_categoria(categoria: schemas.CategoriaCreate, db: Session = Depends(get_db)):
    db_categoria = models.Categoria(nome=categoria.nome)
    db.add(db_categoria)
    db.commit()
    db.refresh(db_categoria)
    return db_categoria

# READ ALL (GET)
@app.get("/api/v1/categorias", response_model=List[schemas.CategoriaResponse])
def listar_categorias(db: Session = Depends(get_db)):
    return db.query(models.Categoria).all()

# READ BY ID (GET)
@app.get("/api/v1/categorias/{categoria_id}", response_model=schemas.CategoriaResponse)
def obter_categoria(categoria_id: int, db: Session = Depends(get_db)):
    categoria = db.query(models.Categoria).filter(models.Categoria.id == categoria_id).first()
    if not categoria:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Categoria não encontrada.")
    return categoria

# UPDATE (PUT)
@app.put("/api/v1/categorias/{categoria_id}", response_model=schemas.CategoriaResponse)
def atualizar_categoria(categoria_id: int, categoria_data: schemas.CategoriaUpdate, db: Session = Depends(get_db)):
    db_categoria = db.query(models.Categoria).filter(models.Categoria.id == categoria_id).first()
    if not db_categoria:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Categoria não encontrada.")
    
    if categoria_data.nome is not None:
        db_categoria.nome = categoria_data.nome

    db.commit()
    db.refresh(db_categoria)
    return db_categoria

# DELETE (DELETE)
@app.delete("/api/v1/categorias/{categoria_id}", status_code=status.HTTP_204_NO_CONTENT)
def deletar_categoria(categoria_id: int, db: Session = Depends(get_db)):
    db_categoria = db.query(models.Categoria).filter(models.Categoria.id == categoria_id).first()
    if not db_categoria:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Categoria não encontrada.")
    
    db.delete(db_categoria)
    db.commit()
    return None


# ==========================================
# 2. ENTIDADE USUÁRIOS (CRUD Completo)
# ==========================================

# CREATE (POST)
@app.post("/api/v1/usuarios", response_model=schemas.UsuarioResponse, status_code=status.HTTP_201_CREATED)
def criar_usuario(usuario: schemas.UsuarioCreate, db: Session = Depends(get_db)):
    usuario_existente = db.query(models.Usuario).filter(models.Usuario.email == usuario.email).first()
    if usuario_existente:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="E-mail já cadastrado.")

    db_usuario = models.Usuario(
        nome=usuario.nome,
        email=usuario.email,
        senha_hash=usuario.senha,
        perfil=usuario.perfil or "PARTICIPANTE"
    )
    db.add(db_usuario)
    db.commit()
    db.refresh(db_usuario)
    return db_usuario

# READ ALL (GET)
@app.get("/api/v1/usuarios", response_model=List[schemas.UsuarioResponse])
def listar_usuarios(db: Session = Depends(get_db)):
    return db.query(models.Usuario).all()

# READ BY ID (GET)
@app.get("/api/v1/usuarios/{usuario_id}", response_model=schemas.UsuarioResponse)
def obter_usuario(usuario_id: int, db: Session = Depends(get_db)):
    usuario = db.query(models.Usuario).filter(models.Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado.")
    return usuario

# UPDATE (PUT)
@app.put("/api/v1/usuarios/{usuario_id}", response_model=schemas.UsuarioResponse)
def atualizar_usuario(usuario_id: int, usuario_data: schemas.UsuarioUpdate, db: Session = Depends(get_db)):
    db_usuario = db.query(models.Usuario).filter(models.Usuario.id == usuario_id).first()
    if not db_usuario:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado.")

    if usuario_data.email is not None and usuario_data.email != db_usuario.email:
        email_em_uso = db.query(models.Usuario).filter(models.Usuario.email == usuario_data.email).first()
        if email_em_uso:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="E-mail já cadastrado por outro usuário.")
        db_usuario.email = usuario_data.email

    if usuario_data.nome is not None:
        db_usuario.nome = usuario_data.nome
    if usuario_data.senha is not None:
        db_usuario.senha_hash = usuario_data.senha
    if usuario_data.perfil is not None:
        db_usuario.perfil = usuario_data.perfil

    db.commit()
    db.refresh(db_usuario)
    return db_usuario

# DELETE (DELETE)
@app.delete("/api/v1/usuarios/{usuario_id}", status_code=status.HTTP_204_NO_CONTENT)
def deletar_usuario(usuario_id: int, db: Session = Depends(get_db)):
    db_usuario = db.query(models.Usuario).filter(models.Usuario.id == usuario_id).first()
    if not db_usuario:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado.")

    db.delete(db_usuario)
    db.commit()
    return None


# ==========================================
# 3. ENTIDADE EVENTOS (CRUD Completo)
# ==========================================

# CREATE (POST)
@app.post("/api/v1/eventos", response_model=schemas.EventoResponse, status_code=status.HTTP_201_CREATED)
def criar_evento(evento: schemas.EventoCreate, db: Session = Depends(get_db)):
    data_evento_naive = evento.data_evento.replace(tzinfo=None) if evento.data_evento.tzinfo else evento.data_evento
    if data_evento_naive < datetime.utcnow():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Não é permitido cadastrar evento com data passada.")

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

# READ ALL (GET)
@app.get("/api/v1/eventos", response_model=List[schemas.EventoResponse])
def listar_eventos(categoria_id: Optional[int] = None, db: Session = Depends(get_db)):
    query = db.query(models.Evento)
    if categoria_id:
        query = query.filter(models.Evento.categoria_id == categoria_id)
    return query.all()

# READ BY ID (GET)
@app.get("/api/v1/eventos/{evento_id}", response_model=schemas.EventoResponse)
def obter_evento(evento_id: int, db: Session = Depends(get_db)):
    evento = db.query(models.Evento).filter(models.Evento.id == evento_id).first()
    if not evento:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Evento não encontrado.")
    return evento

# UPDATE (PUT)
@app.put("/api/v1/eventos/{evento_id}", response_model=schemas.EventoResponse)
def atualizar_evento(evento_id: int, evento_data: schemas.EventoUpdate, db: Session = Depends(get_db)):
    db_evento = db.query(models.Evento).filter(models.Evento.id == evento_id).first()
    if not db_evento:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Evento não encontrado.")

    update_data = evento_data.model_dump(exclude_unset=True)

    if "data_evento" in update_data and update_data["data_evento"]:
        data_naive = update_data["data_evento"].replace(tzinfo=None) if update_data["data_evento"].tzinfo else update_data["data_evento"]
        if data_naive < datetime.utcnow():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Não é permitido alterar a data para o passado.")

    for field, value in update_data.items():
        setattr(db_evento, field, value)

    db.commit()
    db.refresh(db_evento)
    return db_evento

# DELETE (DELETE)
@app.delete("/api/v1/eventos/{evento_id}", status_code=status.HTTP_204_NO_CONTENT)
def deletar_evento(evento_id: int, db: Session = Depends(get_db)):
    db_evento = db.query(models.Evento).filter(models.Evento.id == evento_id).first()
    if not db_evento:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Evento não encontrado.")

    db.delete(db_evento)
    db.commit()
    return None


# ==========================================
# 4. INSCRIÇÕES E CERTIFICADOS (Ações)
# ==========================================

@app.post("/api/v1/inscricoes", response_model=schemas.InscricaoResponse, status_code=status.HTTP_201_CREATED)
def realizar_inscricao(inscricao: schemas.InscricaoCreate, db: Session = Depends(get_db)):
    evento = db.query(models.Evento).filter(models.Evento.id == inscricao.evento_id).first()
    if not evento:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Evento não encontrado.")

    usuario = db.query(models.Usuario).filter(models.Usuario.id == inscricao.usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado.")

    inscricao_existente = db.query(models.Inscricao).filter(
        models.Inscricao.usuario_id == inscricao.usuario_id,
        models.Inscricao.evento_id == inscricao.evento_id
    ).first()
    if inscricao_existente:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Usuário já está inscrito neste evento.")

    total_inscritos = db.query(models.Inscricao).filter(models.Inscricao.evento_id == inscricao.evento_id).count()
    if total_inscritos >= evento.capacidade:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Evento lotado. Capacidade máxima atingida.")

    db_inscricao = models.Inscricao(**inscricao.model_dump())
    db.add(db_inscricao)
    db.commit()
    db.refresh(db_inscricao)
    return db_inscricao


@app.post("/api/v1/certificados", response_model=schemas.CertificadoResponse, status_code=status.HTTP_201_CREATED)
def emitir_certificado(certificado: schemas.CertificadoCreate, db: Session = Depends(get_db)):
    inscricao = db.query(models.Inscricao).filter(models.Inscricao.id == certificado.inscricao_id).first()
    if not inscricao:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inscrição não encontrada.")

    certificado_existente = db.query(models.Certificado).filter(models.Certificado.inscricao_id == certificado.inscricao_id).first()
    if certificado_existente:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Certificado já emitido para esta inscrição.")

    codigo_unico = f"CERT-{uuid.uuid4().hex[:10].upper()}"

    db_certificado = models.Certificado(
        inscricao_id=certificado.inscricao_id,
        codigo_validacao=codigo_unico
    )
    db.add(db_certificado)
    db.commit()
    db.refresh(db_certificado)
    return db_certificado