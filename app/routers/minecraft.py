from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from app.core.auth import require_roles, TokenData
from app.services.rcon_service import rcon_service
from app.core.command_validator import (
    validate_command, 
    get_allowed_commands,
    get_command_examples
)

router = APIRouter(
    prefix="/minecraft",
    tags=["Minecraft"]
)


# =====================
# SCHEMAS
# =====================

class CommandRequest(BaseModel):
    command: str


class MessageRequest(BaseModel):
    message: str


# =====================
# STATUS & PLAYERS
# =====================

@router.get("/players")
def get_players(
    _: TokenData = Depends(require_roles(["admin", "operator", "viewer"]))
):
    """Obtiene lista de jugadores conectados"""
    try:
        player_data = rcon_service.get_player_list()
        return player_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =====================
# GENERIC COMMAND
# =====================

@router.post("/command")
def run_command(
    data: CommandRequest,
    user: TokenData = Depends(require_roles(["admin", "operator"]))
):
    """Ejecuta un comando RCON genérico (validado)"""
    
    # Validar comando
    if not validate_command(data.command, user.roles):
        raise HTTPException(
            status_code=403,
            detail=f"Comando no permitido para tu rol: {data.command}"
        )
    
    try:
        result = rcon_service.execute(data.command)
        return {
            "success": True,
            "command": data.command,
            "executed_by": user.username,
            "response": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =====================
# ALLOWED COMMANDS
# =====================

@router.get("/commands/allowed")
def get_user_allowed_commands(
    user: TokenData = Depends(require_roles(["admin", "operator"]))
):
    """Retorna comandos permitidos para el usuario actual"""
    allowed = get_allowed_commands(user.roles)
    examples = get_command_examples()
    
    return {
        "allowed_patterns": allowed,
        "examples": examples,
        "user_roles": user.roles
    }


# =====================
# BROADCAST MESSAGE
# =====================

@router.post("/message")
def send_broadcast_message(
    data: MessageRequest,
    user: TokenData = Depends(require_roles(["admin", "operator"]))
):
    """Envía mensaje broadcast a todos los jugadores"""
    try:
        response = rcon_service.send_message(data.message)
        return {
            "success": True,
            "message": data.message,
            "sent_by": user.username,
            "response": response
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =====================
# WHITELIST
# =====================

@router.post("/whitelist/add/{player}")
def whitelist_add(
    player: str,
    _: TokenData = Depends(require_roles(["admin", "operator"]))
):
    """Agrega jugador a whitelist"""
    try:
        response = rcon_service.whitelist_add(player)
        return {"success": True, "player": player, "response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/whitelist/remove/{player}")
def whitelist_remove(
    player: str,
    _: TokenData = Depends(require_roles(["admin"]))
):
    """Remueve jugador de whitelist"""
    try:
        response = rcon_service.whitelist_remove(player)
        return {"success": True, "player": player, "response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =====================
# KICK
# =====================

@router.post("/kick/{player}")
def kick_player(
    player: str,
    reason: str = "Kicked by admin",
    _: TokenData = Depends(require_roles(["admin", "operator"]))
):
    """Expulsa a un jugador"""
    try:
        response = rcon_service.kick_player(player, reason)
        return {"success": True, "player": player, "reason": reason, "response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =====================
# BAN
# =====================

@router.post("/ban/{player}")
def ban_player(
    player: str,
    reason: str = "Banned by admin",
    _: TokenData = Depends(require_roles(["admin"]))
):
    """Banea a un jugador"""
    try:
        response = rcon_service.ban_player(player, reason)
        return {"success": True, "player": player, "reason": reason, "response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/pardon/{player}")
def pardon_player(
    player: str,
    _: TokenData = Depends(require_roles(["admin"]))
):
    """Remueve ban de un jugador"""
    try:
        response = rcon_service.pardon_player(player)
        return {"success": True, "player": player, "response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))