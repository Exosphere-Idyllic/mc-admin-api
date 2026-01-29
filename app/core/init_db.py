from app.core.database import engine, Base
from app.models.user import User 

def init_db():
    Base.metadata.create_all(bind=engine)
    print("Base de datos creada")
