from fastapi import APIRouter, Depends, HTTPException, Query
from app.core.auth import require_roles, TokenData
from app.services.systemd_service import systemd_service

router = APIRouter(
    prefix="/system",
    tags=["System"]
)


# ==================
# MINECRAFT SERVICE
# ==================

@router.get("/minecraft/status")
def minecraft_status(
    _: TokenData = Depends(require_roles(["admin", "operator", "viewer"]))
):
    """Obtiene el estado del servicio Minecraft"""
    try:
        return systemd_service.status("minecraft")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/minecraft/start")
def minecraft_start(
    _: TokenData = Depends(require_roles(["admin", "operator"]))
):
    """Inicia el servidor Minecraft"""
    try:
        return systemd_service.start("minecraft")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/minecraft/stop")
def minecraft_stop(
    _: TokenData = Depends(require_roles(["admin"]))
):
    """Detiene el servidor Minecraft (solo admin)"""
    try:
        return systemd_service.stop("minecraft")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/minecraft/restart")
def minecraft_restart(
    _: TokenData = Depends(require_roles(["admin", "operator"]))
):
    """Reinicia el servidor Minecraft"""
    try:
        return systemd_service.restart("minecraft")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/minecraft/logs")
def minecraft_logs(
    lines: int = Query(100, ge=1, le=1000, description="Número de líneas"),
    _: TokenData = Depends(require_roles(["admin", "operator", "viewer"]))
):
    """Obtiene los logs del servidor Minecraft"""
    try:
        logs = systemd_service.get_logs("minecraft", lines)
        return {
            "service": "minecraft",
            "lines": lines,
            "logs": logs.split("\n") if logs else []
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/minecraft/uptime")
def minecraft_uptime(
    _: TokenData = Depends(require_roles(["admin", "operator", "viewer"]))
):
    """Obtiene el uptime del servidor Minecraft"""
    try:
        uptime_seconds = systemd_service.get_uptime("minecraft")
        
        # Convertir segundos a formato legible
        days = uptime_seconds // 86400
        hours = (uptime_seconds % 86400) // 3600
        minutes = (uptime_seconds % 3600) // 60
        seconds = uptime_seconds % 60
        
        return {
            "service": "minecraft",
            "uptime_seconds": uptime_seconds,
            "uptime_formatted": f"{days}d {hours}h {minutes}m {seconds}s"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================
# PLAYIT SERVICE
# ==================

@router.get("/playit/status")
def playit_status(
    _: TokenData = Depends(require_roles(["admin", "operator", "viewer"]))
):
    """Obtiene el estado del servicio Playit"""
    try:
        return systemd_service.status("playit")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/playit/start")
def playit_start(
    _: TokenData = Depends(require_roles(["admin", "operator"]))
):
    """Inicia el agente Playit"""
    try:
        return systemd_service.start("playit")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/playit/stop")
def playit_stop(
    _: TokenData = Depends(require_roles(["admin"]))
):
    """Detiene el agente Playit"""
    try:
        return systemd_service.stop("playit")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/playit/restart")
def playit_restart(
    _: TokenData = Depends(require_roles(["admin", "operator"]))
):
    """Reinicia el agente Playit"""
    try:
        return systemd_service.restart("playit")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/playit/logs")
def playit_logs(
    lines: int = Query(100, ge=1, le=1000),
    _: TokenData = Depends(require_roles(["admin", "operator", "viewer"]))
):
    """Obtiene los logs del agente Playit"""
    try:
        logs = systemd_service.get_logs("playit", lines)
        return {
            "service": "playit",
            "lines": lines,
            "logs": logs.split("\n") if logs else []
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================
# GENERAL STATUS
# ==================

@router.get("/status")
def system_status(
    _: TokenData = Depends(require_roles(["admin", "operator", "viewer"]))
):
    """Obtiene el estado de todos los servicios"""
    try:
        minecraft = systemd_service.status("minecraft")
        playit = systemd_service.status("playit")
        
        return {
            "minecraft": minecraft,
            "playit": playit,
            "all_active": minecraft["active"] and playit["active"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))