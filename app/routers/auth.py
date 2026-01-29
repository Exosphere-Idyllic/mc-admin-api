from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.core.database import get_db
from app.core.auth import authenticate_user, create_access_token

# Esquema para aceptar JSON
class LoginRequest(BaseModel):
    username: str
    password: str

router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)

@router.post("/login")
def login(
    login_data: LoginRequest, # Cambiado de OAuth2PasswordRequestForm a nuestro esquema JSON
    db: Session = Depends(get_db)
):
    # Usamos login_data.username y login_data.password
    user = authenticate_user(db, login_data.username, login_data.password)

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Usuario o contraseña incorrectos"
        )

    access_token = create_access_token(
        data={
            "sub": user.username,
            "roles": user.roles
        }
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }