from fastapi import FastAPI
from app.routers import auth, minecraft, users, system, hardware
from app.core.init_db import init_db

app = FastAPI(
    title="MC Admin API",
    version="0.1.0",
    description="API de administración para servidores Minecraft"
)

# =========================
# ROUTERS
# =========================

app.include_router(auth.router)
app.include_router(minecraft.router)
app.include_router(users.router)
app.include_router(system.router)
app.include_router(hardware.router)

# =========================
# STARTUP
# =========================

@app.on_event("startup")
def on_startup():
    init_db()

# =========================
# HEALTHCHECK
# =========================

@app.get("/health", tags=["System"])
def health_check():
    return {"status": "ok"}
