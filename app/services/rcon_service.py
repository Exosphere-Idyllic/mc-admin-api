import asyncio
from rcon.source import rcon 
from typing import Dict, List
import re
from app.core.config import settings

class RCONService:
    def __init__(self):
        self.host = settings.RCON_HOST
        self.port = settings.RCON_PORT
        self.password = settings.RCON_PASSWORD

    async def execute(self, command: str) -> str:
        try:
            response = await rcon(
                command, 
                host=self.host, 
                port=self.port, 
                passwd=self.password,
                timeout=5
            )
            return response if response else ""
        except Exception as e:
            print(f"Error en RCON execute: {e}")
            return f"Error: {str(e)}"

    async def get_player_list(self) -> Dict:
        """Obtiene lista de jugadores limpiando códigos de color (§)"""
        try:
            raw_response = await self.execute("list")
            
            # 1. LIMPIEZA: Eliminamos los códigos de color (§ seguido de cualquier carácter)
            # Esto transforma "§6There are §c0" en "There are 0"
            clean_response = re.sub(r'§.', '', raw_response)
            
            # 2. EXTRAER NÚMEROS: Ahora que el texto está limpio de símbolos raros
            numbers = re.findall(r'\d+', clean_response)
            
            online = int(numbers[0]) if len(numbers) > 0 else 0
            # Si el servidor dice "0 out of 20", online=0, max=20
            max_players = int(numbers[1]) if len(numbers) > 1 else 20
            
            # 3. EXTRAER NOMBRES
            players = []
            if ":" in clean_response:
                parts = clean_response.split(":", 1)
                if len(parts) > 1 and parts[1].strip():
                    players = [p.strip() for p in parts[1].split(",") if p.strip()]
            
            return {
                "online": online,
                "max": max_players,
                "players": players
            }
            
        except Exception as e:
            print(f"Error parseando lista de jugadores: {e}")
            return {"online": 0, "max": 20, "players": [], "error": str(e)}

    async def send_message(self, message: str) -> str:
        return await self.execute(f"say {message}")

    async def kick_player(self, player: str, reason: str = "") -> str:
        return await self.execute(f"kick {player} {reason}".strip())

    async def ban_player(self, player: str, reason: str = "") -> str:
        return await self.execute(f"ban {player} {reason}".strip())

    async def pardon_player(self, player: str) -> str:
        return await self.execute(f"pardon {player}")

    async def make_op(self, player: str) -> str:
        return await self.execute(f"op {player}")

    async def deop_player(self, player: str) -> str:
        return await self.execute(f"deop {player}")

    async def whitelist_add(self, player: str) -> str:
        return await self.execute(f"whitelist add {player}")

    async def whitelist_remove(self, player: str) -> str:
        return await self.execute(f"whitelist remove {player}")

rcon_service = RCONService()