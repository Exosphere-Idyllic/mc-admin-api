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
async def get_players():
    """Obtiene la lista de jugadores conectados de forma asíncrona"""
    return await rcon_service.get_player_list()

@router.post("/op/{player}")
async def make_op(
    player: str,
    _: TokenData = Depends(require_roles(["admin"]))
):
    try:
        response = await rcon_service.make_op(player)
        return {"success": True, "player": player, "response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
# =====================
# GENERIC COMMAND
# =====================

@router.post("/command")
async def run_command(
    data: CommandRequest,
    user: TokenData = Depends(require_roles(["admin", "operator"]))
):
    """Ejecuta un comando RCON genérico (validado)"""
    
    # Validar comando según el rol del usuario
    if not validate_command(data.command, user.roles):
        raise HTTPException(
            status_code=403,
            detail=f"Comando no permitido para tu rol: {data.command}"
        )
    
    try:
        # Usamos await porque la comunicación de red es asíncrona
        result = await rcon_service.execute(data.command)
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
    """Retorna comandos permitidos (Síncrono ya que no requiere RCON)"""
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
async def send_broadcast_message(
    data: MessageRequest,
    user: TokenData = Depends(require_roles(["admin", "operator"]))
):
    """Envía mensaje broadcast a todos los jugadores"""
    try:
        response = await rcon_service.send_message(data.message)
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
async def whitelist_add(
    player: str,
    _: TokenData = Depends(require_roles(["admin", "operator"]))
):
    try:
        response = await rcon_service.whitelist_add(player)
        return {"success": True, "player": player, "response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/whitelist/remove/{player}")
async def whitelist_remove(
    player: str,
    _: TokenData = Depends(require_roles(["admin"]))
):
    try:
        response = await rcon_service.whitelist_remove(player)
        return {"success": True, "player": player, "response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# =====================
# KICK
# =====================

@router.post("/kick/{player}")
async def kick_player(
    player: str,
    reason: str = "Expulsado por el administrador",
    _: TokenData = Depends(require_roles(["admin", "operator"]))
):
    try:
        response = await rcon_service.kick_player(player, reason)
        return {"success": True, "player": player, "reason": reason, "response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# =====================
# BAN
# =====================

@router.post("/ban/{player}")
async def ban_player(
    player: str,
    reason: str = "Baneado por el administrador",
    _: TokenData = Depends(require_roles(["admin"]))
):
    try:
        response = await rcon_service.ban_player(player, reason)
        return {"success": True, "player": player, "reason": reason, "response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/pardon/{player}")
async def pardon_player(
    player: str,
    _: TokenData = Depends(require_roles(["admin"]))
):
    try:
        response = await rcon_service.pardon_player(player)
        return {"success": True, "player": player, "response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))