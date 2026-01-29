import subprocess
from typing import Literal, Dict
from app.core.config import settings

ServiceName = Literal["minecraft", "playit"]


class SystemdService:
    """Servicio para gestionar servicios systemd (Minecraft y Playit)"""
    
    def __init__(self):
        self.minecraft_service = settings.MINECRAFT_SERVICE
        self.playit_service = settings.PLAYIT_SERVICE
    
    def _run_systemctl(self, action: str, service: str) -> str:
        try:
            # Usamos la ruta completa /usr/bin/systemctl
            result = subprocess.run(
                ["sudo", "/usr/bin/systemctl", action, service],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode != 0 and action not in ["is-active", "status"]:
                raise RuntimeError(result.stderr or "Error ejecutando systemctl")
            
            return result.stdout.strip()
            
        except subprocess.TimeoutExpired:
            raise RuntimeError(f"Timeout ejecutando: systemctl {action} {service}")
        except FileNotFoundError:
            # Si /usr/bin/ no funciona, intentamos /bin/
            try:
                result = subprocess.run(["sudo", "/bin/systemctl", action, service], capture_output=True, text=True, timeout=10)
                return result.stdout.strip()
            except:
                raise RuntimeError("systemctl no encontrado en /usr/bin/ ni /bin/")
    
    def start(self, service: ServiceName) -> Dict:
        """Inicia un servicio"""
        service_name = self.minecraft_service if service == "minecraft" else self.playit_service
        self._run_systemctl("start", service_name)
        return {
            "success": True, 
            "action": "start", 
            "service": service
        }
    
    def stop(self, service: ServiceName) -> Dict:
        """Detiene un servicio"""
        service_name = self.minecraft_service if service == "minecraft" else self.playit_service
        self._run_systemctl("stop", service_name)
        return {
            "success": True, 
            "action": "stop", 
            "service": service
        }
    
    def restart(self, service: ServiceName) -> Dict:
        """Reinicia un servicio"""
        service_name = self.minecraft_service if service == "minecraft" else self.playit_service
        self._run_systemctl("restart", service_name)
        return {
            "success": True, 
            "action": "restart", 
            "service": service
        }
    
    def status(self, service: ServiceName) -> Dict:
        """Obtiene estado de un servicio"""
        service_name = self.minecraft_service if service == "minecraft" else self.playit_service
        
        try:
            output = self._run_systemctl("is-active", service_name)
            is_active = output == "active"
            
            return {
                "service": service,
                "active": is_active,
                "state": output
            }
        except RuntimeError:
            return {
                "service": service,
                "active": False,
                "state": "inactive"
            }
    
    def get_logs(self, service: ServiceName, lines: int = 100) -> str:
        service_name = self.minecraft_service if service == "minecraft" else self.playit_service
        try:
            # Usamos la ruta completa /usr/bin/journalctl
            result = subprocess.run(
                ["sudo", "/usr/bin/journalctl", "-u", service_name, "-n", str(lines), "--no-pager"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.stdout
        except Exception as e:
            raise RuntimeError(f"Error obteniendo logs: {e}")
    
    def get_uptime(self, service: ServiceName) -> int:
        """
        Obtiene uptime del servicio en segundos
        
        Returns:
            Segundos desde que el servicio está activo
        """
        service_name = self.minecraft_service if service == "minecraft" else self.playit_service
        
        try:
            result = subprocess.run(
                ["systemctl", "show", service_name, "--property=ActiveEnterTimestamp"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            timestamp_line = result.stdout.strip()
            if not timestamp_line or "=" not in timestamp_line:
                return 0
            
            timestamp_str = timestamp_line.split("=")[1].strip()
            if not timestamp_str or timestamp_str == "n/a":
                return 0
            
            from datetime import datetime
            start_time = datetime.strptime(timestamp_str, "%a %Y-%m-%d %H:%M:%S %Z")
            uptime = (datetime.now() - start_time).total_seconds()
            
            return int(uptime)
            
        except Exception:
            return 0


# Singleton instance
systemd_service = SystemdService()