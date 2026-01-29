from rcon.source import Client
from contextlib import contextmanager
from typing import Dict, List
import re
from app.core.config import settings


class RCONService:
    """Servicio para gestionar conexiones RCON al servidor Minecraft"""
    
    def __init__(self):
        self.host = settings.RCON_HOST
        self.port = settings.RCON_PORT
        self.password = settings.RCON_PASSWORD
    
    @contextmanager
    def get_client(self):
        """Context manager para manejar conexiones RCON"""
        client = None
        try:
            client = Client(
                self.host, 
                self.port, 
                passwd=self.password, 
                timeout=5
            )
            yield client
        except ConnectionRefusedError:
            raise RuntimeError("No se pudo conectar al servidor RCON. ¿Está el servidor en línea?")
        except Exception as e:
            raise RuntimeError(f"Error RCON: {e}")
        finally:
            if client:
                try:
                    client.close()
                except:
                    pass
    
    def execute(self, command: str) -> str:
        """
        Ejecuta un comando RCON
        
        Args:
            command: Comando de consola de Minecraft
            
        Returns:
            Respuesta del servidor
        """
        with self.get_client() as client:
            response = client.run(command)
            return response
    
    def get_player_list(self) -> Dict:
        """
        Obtiene lista de jugadores conectados
        
        Returns:
            Dict con: online (int), max (int), players (list)
        """
        try:
            response = self.execute("list")
            # Parse: "There are 3 of a max of 20 players online: Player1, Player2, Player3"
            
            if "There are" in response:
                parts = response.split(":")
                count_part = parts[0]
                
                # Extraer números
                numbers = re.findall(r'\d+', count_part)
                online = int(numbers[0]) if len(numbers) > 0 else 0
                max_players = int(numbers[1]) if len(numbers) > 1 else 20
                
                # Extraer nombres de jugadores
                players = []
                if len(parts) > 1 and parts[1].strip():
                    players = [p.strip() for p in parts[1].split(",")]
                
                return {
                    "online": online,
                    "max": max_players,
                    "players": players
                }
            
            return {"online": 0, "max": 20, "players": []}
            
        except Exception as e:
            return {
                "online": 0, 
                "max": 20, 
                "players": [], 
                "error": str(e)
            }
    
    def send_message(self, message: str) -> str:
        """Envía mensaje broadcast a todos los jugadores"""
        return self.execute(f"say {message}")
    
    def kick_player(self, player: str, reason: str = "") -> str:
        """Expulsa a un jugador"""
        cmd = f"kick {player} {reason}".strip()
        return self.execute(cmd)
    
    def whitelist_add(self, player: str) -> str:
        """Agrega jugador a whitelist"""
        return self.execute(f"whitelist add {player}")
    
    def whitelist_remove(self, player: str) -> str:
        """Remueve jugador de whitelist"""
        return self.execute(f"whitelist remove {player}")
    
    def ban_player(self, player: str, reason: str = "") -> str:
        """Banea a un jugador"""
        cmd = f"ban {player} {reason}".strip()
        return self.execute(cmd)
    
    def pardon_player(self, player: str) -> str:
        """Remueve ban de un jugador"""
        return self.execute(f"pardon {player}")


# Singleton instance
rcon_service = RCONService()