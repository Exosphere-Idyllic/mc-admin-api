from pydantic import BaseModel
from typing import Optional, List

class UserBase(BaseModel):
    username: str
    roles: str  # "admin,operator"

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    password: Optional[str] = None
    roles: Optional[str] = None

class UserOut(UserBase):
    id: int

    class Config:
        from_attributes = True
