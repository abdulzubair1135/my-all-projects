import socket
import subprocess
import time
import psutil
import os
from pathlib import Path
from typing import Optional, Dict, Any

class ProcessManager:
    """
    Manages background server processes (uvicorn, node, etc.), port allocation,
    health polling, and clean shutdowns.
    """
    def __init__(self):
        self.active_processes: Dict[str, subprocess.Popen] = {}
        self.process_logs: Dict[str, Path] = {}

    @staticmethod
    def find_free_port(start_port: int = 8000, max_port: int = 8100) -> int:
        """
        Finds an available TCP port.
        """
        for port in range(start_port, max_port):
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                try:
                    s.bind(("127.0.0.1", port))
                    return port
                except OSError:
                    continue
        return start_port

    @staticmethod
    def kill_process_on_port(port: int):
        """
        Finds any process listening on the given port and forcefully terminates it
        (including its process tree) so the new app can take over cleanly.
        """
        if os.name == 'nt':
            try:
                out = subprocess.check_output(f'netstat -ano | findstr :{port}', shell=True, text=True, errors='ignore')
                pids = set()
                for line in out.strip().splitlines():
                    parts = line.split()
                    if len(parts) >= 5 and "LISTENING" in parts:
                        pid = parts[-1]
                        if pid.isdigit() and int(pid) > 0:
                            pids.add(int(pid))
                for pid in pids:
                    subprocess.run(f"taskkill /F /T /PID {pid}", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                time.sleep(0.5)
            except Exception:
                pass

        try:
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    conn_func = getattr(proc, 'net_connections', None) or getattr(proc, 'connections', None)
                    if conn_func:
                        for conn in conn_func(kind='inet'):
                            if conn.laddr and conn.laddr.port == port:
                                proc.kill()
                                time.sleep(0.3)
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    pass
        except Exception:
            pass

    def is_port_open(self, port: int, host: str = "127.0.0.1") -> bool:
        """
        Checks if a port is currently listening.
        """
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1.0)
            return s.connect_ex((host, port)) == 0

    def start_server(
        self,
        name: str,
        command: str,
        port: int,
        cwd: Optional[str | Path] = None,
        log_dir: Optional[str | Path] = None,
        startup_timeout: int = 15
    ) -> Dict[str, Any]:
        """
        Starts a background server process, redirects logs, and waits for the port to become active.
        """
        self.stop_server(name)
        self.kill_process_on_port(port)

        work_dir = Path(cwd) if cwd else Path.cwd()
        log_path = Path(log_dir) if log_dir else (work_dir / ".omnidev_logs")
        log_path.mkdir(parents=True, exist_ok=True)
        log_file = log_path / f"{name}_server.log"

        out_fd = open(log_file, "w", encoding="utf-8")
        proc = subprocess.Popen(
            command,
            cwd=str(work_dir),
            shell=True,
            stdout=out_fd,
            stderr=subprocess.STDOUT,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0
        )

        self.active_processes[name] = proc
        self.process_logs[name] = log_file

        # Poll until port is open or process exits
        start_time = time.time()
        while time.time() - start_time < startup_timeout:
            if proc.poll() is not None:
                # Process exited prematurely
                out_fd.close()
                log_content = log_file.read_text(encoding="utf-8", errors="ignore") if log_file.exists() else ""
                return {
                    "success": False,
                    "error": f"Process exited with code {proc.returncode}.\nLogs:\n{log_content}",
                    "port": port,
                    "pid": proc.pid
                }

            if self.is_port_open(port):
                out_fd.close()
                return {
                    "success": True,
                    "url": f"http://127.0.0.1:{port}",
                    "port": port,
                    "pid": proc.pid,
                    "log_file": str(log_file)
                }
            time.sleep(0.5)

        # Timeout reached
        out_fd.close()
        log_content = log_file.read_text(encoding="utf-8", errors="ignore") if log_file.exists() else ""
        return {
            "success": False,
            "error": f"Server failed to open port {port} within {startup_timeout} seconds.\nLogs:\n{log_content}",
            "port": port,
            "pid": proc.pid
        }

    def get_logs(self, name: str) -> str:
        if name in self.process_logs and self.process_logs[name].exists():
            return self.process_logs[name].read_text(encoding="utf-8", errors="ignore")
        return ""

    def stop_server(self, name: str):
        """
        Safely terminates a running server process and all child processes.
        """
        if name in self.active_processes:
            proc = self.active_processes[name]
            try:
                parent = psutil.Process(proc.pid)
                for child in parent.children(recursive=True):
                    child.kill()
                parent.kill()
            except Exception:
                try:
                    proc.kill()
                except Exception:
                    pass
            del self.active_processes[name]

    def stop_all(self):
        for name in list(self.active_processes.keys()):
            self.stop_server(name)
