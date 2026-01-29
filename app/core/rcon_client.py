from rcon.source import Client
import os

RCON_HOST = os.getenv("RCON_HOST", "127.0.0.1")
RCON_PORT = int(os.getenv("RCON_PORT", 25575))
RCON_PASSWORD = os.getenv("RCON_PASSWORD", "Talos11")


def send_rcon_command(command: str) -> str:
    try:
        with Client(
            RCON_HOST,
            RCON_PORT,
            passwd=RCON_PASSWORD,
            timeout=5
        ) as client:
            response = client.run(command)
            return response
    except Exception as e:
        raise RuntimeError(f"RCON error: {e}")
