from fastapi import APIRouter, Depends, HTTPException
from app.core.auth import require_roles, TokenData
import subprocess
import psutil
from datetime import datetime

router = APIRouter(
    prefix="/hardware",
    tags=["Hardware"]
)


# ==================
# TEMPERATURE
# ==================

@router.get("/temperature")
def get_temperature(
    _: TokenData = Depends(require_roles(["admin", "operator", "viewer"]))
):
    """Obtiene la temperatura del CPU (Raspberry Pi)"""
    try:
        result = subprocess.run(
            ["vcgencmd", "measure_temp"],
            capture_output=True,
            text=True,
            timeout=2
        )
        
        if result.returncode != 0:
            return {"error": "No se pudo obtener temperatura", "available": False}
        
        temp_str = result.stdout.strip()
        # Formato: temp=45.2'C
        temp = float(temp_str.split("=")[1].split("'")[0])
        
        # Determinar estado
        if temp > 80:
            status = "critical"
            message = "⚠️ Temperatura crítica - considerar enfriamiento"
        elif temp > 70:
            status = "hot"
            message = "🔥 Temperatura alta"
        elif temp > 60:
            status = "warm"
            message = "🌡️ Temperatura templada"
        else:
            status = "optimal"
            message = "✅ Temperatura óptima"
        
        return {
            "celsius": round(temp, 1),
            "fahrenheit": round((temp * 9/5) + 32, 1),
            "status": status,
            "message": message,
            "available": True
        }
    
    except FileNotFoundError:
        return {
            "error": "vcgencmd no disponible (no es Raspberry Pi?)",
            "available": False
        }
    except Exception as e:
        return {
            "error": str(e),
            "available": False
        }


# ==================
# CPU FREQUENCY
# ==================

@router.get("/cpu/frequency")
def get_cpu_frequency(
    _: TokenData = Depends(require_roles(["admin", "operator", "viewer"]))
):
    """Obtiene la frecuencia actual del CPU"""
    try:
        result = subprocess.run(
            ["vcgencmd", "measure_clock", "arm"],
            capture_output=True,
            text=True,
            timeout=2
        )
        
        if result.returncode != 0:
            return {"error": "No disponible", "available": False}
        
        # Formato: frequency(48)=600000000
        freq_str = result.stdout.strip()
        frequency = int(freq_str.split("=")[1])
        
        return {
            "hz": frequency,
            "mhz": round(frequency / 1_000_000),
            "ghz": round(frequency / 1_000_000_000, 2),
            "available": True
        }
    
    except Exception as e:
        return {"error": str(e), "available": False}


# ==================
# VOLTAGE
# ==================

@router.get("/cpu/voltage")
def get_voltage(
    _: TokenData = Depends(require_roles(["admin", "operator", "viewer"]))
):
    """Obtiene el voltaje del CPU"""
    try:
        result = subprocess.run(
            ["vcgencmd", "measure_volts", "core"],
            capture_output=True,
            text=True,
            timeout=2
        )
        
        if result.returncode != 0:
            return {"error": "No disponible", "available": False}
        
        # Formato: volt=1.2000V
        volt_str = result.stdout.strip()
        voltage = float(volt_str.split("=")[1].replace("V", ""))
        
        return {
            "volts": voltage,
            "status": "undervolt" if voltage < 1.2 else "normal",
            "available": True
        }
    
    except Exception as e:
        return {"error": str(e), "available": False}


# ==================
# SYSTEM RESOURCES
# ==================

@router.get("/resources")
def get_resources(
    _: TokenData = Depends(require_roles(["admin", "operator", "viewer"]))
):
    """Obtiene uso de recursos del sistema (CPU, RAM, Disco)"""
    try:
        # CPU
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_count = psutil.cpu_count()
        
        # Memoria
        memory = psutil.virtual_memory()
        
        # Disco
        disk = psutil.disk_usage('/')
        
        # Uptime del sistema
        boot_time = psutil.boot_time()
        uptime_seconds = int(datetime.now().timestamp() - boot_time)
        
        days = uptime_seconds // 86400
        hours = (uptime_seconds % 86400) // 3600
        minutes = (uptime_seconds % 3600) // 60
        
        return {
            "cpu": {
                "percent": round(cpu_percent, 1),
                "count": cpu_count,
                "status": "high" if cpu_percent > 80 else "normal"
            },
            "memory": {
                "total_mb": round(memory.total / (1024**2)),
                "used_mb": round(memory.used / (1024**2)),
                "available_mb": round(memory.available / (1024**2)),
                "percent": memory.percent,
                "status": "high" if memory.percent > 85 else "normal"
            },
            "disk": {
                "total_gb": round(disk.total / (1024**3), 1),
                "used_gb": round(disk.used / (1024**3), 1),
                "free_gb": round(disk.free / (1024**3), 1),
                "percent": disk.percent,
                "status": "high" if disk.percent > 85 else "normal"
            },
            "uptime": {
                "seconds": uptime_seconds,
                "formatted": f"{days}d {hours}h {minutes}m"
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================
# THROTTLE STATUS
# ==================

@router.get("/throttle")
def get_throttle_status(
    _: TokenData = Depends(require_roles(["admin", "operator", "viewer"]))
):
    """Verifica si el sistema ha sido throttled por temperatura o bajo voltaje"""
    try:
        result = subprocess.run(
            ["vcgencmd", "get_throttled"],
            capture_output=True,
            text=True,
            timeout=2
        )
        
        if result.returncode != 0:
            return {"error": "No disponible", "available": False}
        
        # Formato: throttled=0x50000
        throttled_str = result.stdout.strip()
        throttled_hex = throttled_str.split("=")[1]
        value = int(throttled_hex, 16)
        
        return {
            "raw": throttled_hex,
            "current": {
                "under_voltage": bool(value & 0x1),
                "freq_capped": bool(value & 0x2),
                "throttled": bool(value & 0x4),
                "soft_temp_limit": bool(value & 0x8)
            },
            "has_occurred": {
                "under_voltage": bool(value & 0x10000),
                "freq_capped": bool(value & 0x20000),
                "throttled": bool(value & 0x40000),
                "soft_temp_limit": bool(value & 0x80000)
            },
            "status": "healthy" if value == 0 else "issues_detected",
            "available": True
        }
    
    except Exception as e:
        return {"error": str(e), "available": False}


# ==================
# FULL STATS
# ==================

@router.get("/stats")
def get_full_stats(
    _: TokenData = Depends(require_roles(["admin", "operator", "viewer"]))
):
    """Obtiene todas las estadísticas de hardware en un solo endpoint"""
    try:
        temp = get_temperature(_)
        resources = get_resources(_)
        throttle = get_throttle_status(_)
        
        return {
            "temperature": temp,
            "resources": resources,
            "throttle": throttle,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))