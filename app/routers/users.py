from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate, UserOut
from app.core.auth import (
    get_password_hash,
    require_roles,
    TokenData
)

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

# =====================
# LIST USERS (ADMIN)
# =====================
@router.get("/", response_model=list[UserOut])
def list_users(
    db: Session = Depends(get_db),
    _: TokenData = Depends(require_roles(["admin"]))
):
    return db.query(User).all()

# =====================
# CREATE USER (ADMIN)
# =====================
@router.post("/", response_model=UserOut)
def create_user(
    data: UserCreate,
    db: Session = Depends(get_db),
    _: TokenData = Depends(require_roles(["admin"]))
):
    if db.query(User).filter(User.username == data.username).first():
        raise HTTPException(status_code=400, detail="Usuario ya existe")

    user = User(
        username=data.username,
        password_hash=get_password_hash(data.password),
        roles=data.roles
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

# =====================
# UPDATE USER (ADMIN)
# =====================
@router.put("/{user_id}")
def update_user(
    user_id: int,
    data: UserUpdate,
    db: Session = Depends(get_db),
    _: TokenData = Depends(require_roles(["admin"]))
):
    user = db.query(User).get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    if data.password:
        user.password_hash = get_password_hash(data.password)
    if data.roles:
        user.roles = data.roles

    db.commit()
    return {"success": True}

# =====================
# DELETE USER (ADMIN)
# =====================
@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    _: TokenData = Depends(require_roles(["admin"]))
):
    user = db.query(User).get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    db.delete(user)
    db.commit()
    return {"success": True}
