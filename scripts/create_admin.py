from app.core.database import SessionLocal
from app.core.auth import get_password_hash
from app.models.user import User

def create_admin():
    db = SessionLocal()

    if db.query(User).filter(User.username == "admin").first():
        print("⚠️  El usuario admin ya existe")
        return

    admin = User(
        username="admin",
        password_hash=get_password_hash("admin123"),
        roles="admin"
    )

    db.add(admin)
    db.commit()
    db.close()

    print("✅ Usuario admin creado")

if __name__ == "__main__":
    create_admin()
