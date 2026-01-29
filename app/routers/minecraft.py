from fastapi import APIRouter, Depends, HTTPException
from app.core.auth import require_roles, TokenData
from app.core.rcon_client import send_rcon_command

router = APIRouter(
    prefix="/rcon",
    tags=["RCON"]
)

router = APIRouter(
    prefix="/minecraft",
    tags=["Minecraft"]
)


# =========================
# TEST (ADMIN + OPERATOR)
# =========================

@router.get("/test")
def rcon_test(
    user: TokenData = Depends(require_roles(["admin", "operator"]))
):
    try:
        result = send_rcon_command("list")
        return {
            "success": True,
            "executed_by": user.username,
            "roles": user.roles,
            "response": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# =========================
# GENERIC COMMAND
# =========================

@router.post("/command")
def run_command(
    command: str,
    user: TokenData = Depends(require_roles(["admin", "operator"]))
):
    try:
        result = send_rcon_command(command)
        return {
            "success": True,
            "command": command,
            "executed_by": user.username,
            "response": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# =====================
# WHITELIST ADD
# =====================
@router.post("/whitelist/add/{player}")
def whitelist_add(
    player: str,
    _: TokenData = Depends(require_roles(["admin", "operator"]))
):
    send_rcon_command(f"whitelist add {player}")
    return {"success": True}

# =====================
# WHITELIST REMOVE
# =====================
@router.post("/whitelist/remove/{player}")
def whitelist_remove(
    player: str,
    _: TokenData = Depends(require_roles(["admin"]))
):
    send_rcon_command(f"whitelist remove {player}")
    return {"success": True}

# =====================
# KICK
# =====================
@router.post("/kick/{player}")
def kick_player(
    player: str,
    reason: str = "Kicked by admin",
    _: TokenData = Depends(require_roles(["admin", "operator"]))
):
    send_rcon_command(f"kick {player} {reason}")
    return {"success": True}

# =====================
# BAN
# =====================
@router.post("/ban/{player}")
def ban_player(
    player: str,
    reason: str = "Banned by admin",
    _: TokenData = Depends(require_roles(["admin"]))
):
    send_rcon_command(f"ban {player} {reason}")
    return {"success": True}