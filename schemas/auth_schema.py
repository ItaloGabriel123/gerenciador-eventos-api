from pydantic import BaseModel, EmailStr

class TokenSchema(BaseModel):
    access_token: str
    token_type: str = "bearer"

class LoginSchema(BaseModel):
    email: EmailStr
    senha: str