import os
import sys
# Esto asegura que Python encuentre la carpeta 'app'
sys.path.append(os.getcwd())

from app.core.database import SessionLocal, engine, Base
from app.models.user import User
from passlib.context import CryptContext

# Configuramos el hash de contraseña
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Creamos las tablas por si no existen
Base.metadata.create_all(bind=engine)

db = SessionLocal()

try:
    # Verificamos si ya existe el admin
    admin_exists = db.query(User).filter(User.username == "admin").first()
    if not admin_exists:
        hashed_password = pwd_context.hash("admin123")
        # Nota: He puesto 'roles' porque tu auth.py anterior lo usaba en plural
        new_user = User(
            username="admin", 
            hashed_password=hashed_password, 
            roles="admin", 
            is_active=True
        )
        db.add(new_user)
        db.commit()
        print("✅ Usuario 'admin' creado exitosamente en data/admin.db")
    else:
        print("ℹ️ El usuario 'admin' ya existe en la base de datos.")
finally:
    db.close()