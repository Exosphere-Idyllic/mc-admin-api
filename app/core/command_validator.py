from typing import List
from typing import List, Dict 
import re


# Comandos permitidos por rol
ALLOWED_COMMANDS = {
    "operator": [
        r"^list$",
        r"^say .+",
        r"^msg \w+ .+",
        r"^tell \w+ .+",
        r"^whitelist add \w+",
        r"^whitelist remove \w+",
        r"^kick \w+.*",
        r"^tp \w+ \w+",
        r"^tp \w+ \d+ \d+ \d+",
        r"^gamemode (survival|creative|adventure|spectator) \w+",
        r"^time set (day|night|\d+)",
        r"^weather (clear|rain|thunder)",
        r"^give \w+ \w+ \d+",
        r"^effect give \w+ \w+ \d+ \d+",
        r"^effect clear \w+",
        r"^teleport \w+ \w+",
        r"^clear \w+",
    ],
    "admin": [
        r"^stop$",
        r"^save-all$",
        r"^save-on$",
        r"^save-off$",
        r"^ban \w+.*",
        r"^ban-ip \S+.*",
        r"^pardon \w+",
        r"^pardon-ip \S+",
        r"^op \w+",
        r"^deop \w+",
        r"^seed$",
        r"^difficulty (peaceful|easy|normal|hard)",
        r"^whitelist (on|off|list|reload)",
        r"^reload$",
        r"^setblock \d+ \d+ \d+ \w+",
        r"^fill \d+ \d+ \d+ \d+ \d+ \d+ \w+",
    ]
}


def validate_command(command: str, user_roles: str) -> bool:
    """
    Valida si un comando está permitido para los roles del usuario
    
    Args:
        command: Comando a validar
        user_roles: Roles del usuario separados por coma (ej: "admin,operator")
        
    Returns:
        True si el comando está permitido, False si no
    """
    
    roles_list = [r.strip() for r in user_roles.split(",")]
    
    # Admin puede ejecutar todo
    if "admin" in roles_list:
        patterns = ALLOWED_COMMANDS["operator"] + ALLOWED_COMMANDS["admin"]
    elif "operator" in roles_list:
        patterns = ALLOWED_COMMANDS["operator"]
    else:
        # viewer no puede ejecutar comandos
        return False
    
    command_clean = command.strip()
    
    for pattern in patterns:
        if re.match(pattern, command_clean, re.IGNORECASE):
            return True
    
    return False


def get_allowed_commands(user_roles: str) -> Dict[str, List[str]]:
    """
    Retorna lista de comandos permitidos para el usuario
    
    Args:
        user_roles: Roles del usuario separados por coma
        
    Returns:
        Diccionario con comandos permitidos por categoría
    """
    roles_list = [r.strip() for r in user_roles.split(",")]
    
    if "admin" in roles_list:
        return {
            "operator": ALLOWED_COMMANDS["operator"],
            "admin": ALLOWED_COMMANDS["admin"]
        }
    elif "operator" in roles_list:
        return {
            "operator": ALLOWED_COMMANDS["operator"]
        }
    
    return {}


def get_command_examples() -> Dict[str, List[str]]:
    """Retorna ejemplos de comandos útiles"""
    return {
        "Información": [
            "list - Ver jugadores online",
            "seed - Ver seed del mundo",
        ],
        "Comunicación": [
            "say Hola servidor - Mensaje a todos",
            "msg jugador Hola - Mensaje privado",
        ],
        "Teletransporte": [
            "tp jugador1 jugador2 - Teleportar",
            "tp jugador 0 64 0 - TP a coordenadas",
        ],
        "Gamemode": [
            "gamemode survival jugador",
            "gamemode creative jugador",
        ],
        "Tiempo/Clima": [
            "time set day - Día",
            "time set night - Noche",
            "weather clear - Clima despejado",
        ],
        "Whitelist": [
            "whitelist add jugador",
            "whitelist remove jugador",
        ],
        "Admin": [
            "ban jugador motivo",
            "pardon jugador",
            "op jugador",
            "stop - Apagar servidor",
        ]
    }