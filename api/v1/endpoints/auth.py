from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from core.deps import get_db
from core.security import verificar_senha, criar_token_acesso
from models.usuario_model import Usuario
from schemas.auth_schema import TokenSchema

router = APIRouter()

@router.post("/login", response_model=TokenSchema)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(), 
    db: Session = Depends(get_db)
):
    # O OAuth2PasswordRequestForm usa o campo 'username' para enviar o e-mail
    usuario = db.query(Usuario).filter(Usuario.email == form_data.username).first()
    
    if not usuario or not verificar_senha(form_data.password, usuario.senha_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-mail ou palavra-passe incorretos.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = criar_token_acesso(subject=usuario.id)
    return {"access_token": access_token, "token_type": "bearer"}