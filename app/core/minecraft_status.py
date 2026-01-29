import psutil
import time

JAVA_KEYWORDS = ["paper.jar", "java"]


def find_minecraft_process():
    for proc in psutil.process_iter(["pid", "name", "cmdline", "create_time"]):
        try:
            cmdline = " ".join(proc.info["cmdline"] or [])
            if "paper.jar" in cmdline:
                return proc
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return None


def get_process_stats(proc: psutil.Process):
    with proc.oneshot():
        mem = proc.memory_info().rss / (1024 * 1024)
        cpu = proc.cpu_percent(interval=0.1)
        uptime = time.time() - proc.create_time()

    return {
        "pid": proc.pid,
        "memory_mb": round(mem, 1),
        "cpu_percent": round(cpu, 1),
        "uptime_seconds": int(uptime)
    }
