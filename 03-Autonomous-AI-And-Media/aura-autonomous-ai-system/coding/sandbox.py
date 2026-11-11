"""
AURA Coding Sandbox Module.
Provides controlled Python and shell execution with timeouts and process isolation.
"""

import subprocess
import sys
import tempfile
import os
from pathlib import Path
from typing import Dict, Any
from core.logger import setup_logger

logger = setup_logger("CodeSandbox")

class CodeSandbox:
    def execute_python_code(self, code_content: str, timeout: int = 15) -> Dict[str, Any]:
        """
        Executes Python code in an isolated subprocess with timeout enforcement.
        """
        logger.info(f"Executing Python snippet in sandbox (timeout={timeout}s)")
        with tempfile.NamedTemporaryFile(suffix=".py", mode="w", encoding="utf-8", delete=False) as f:
            f.write(code_content)
            temp_path = f.name

        try:
            res = subprocess.run(
                [sys.executable, temp_path],
                capture_output=True,
                text=True,
                timeout=timeout
            )
            stdout = res.stdout.strip()
            stderr = res.stderr.strip()
            success = (res.returncode == 0)

            logger.info(f"Sandbox execution returncode={res.returncode}")
            return {
                "status": "success" if success else "error",
                "returncode": res.returncode,
                "stdout": stdout,
                "stderr": stderr
            }
        except subprocess.TimeoutExpired:
            logger.error(f"Sandbox execution timed out after {timeout}s")
            return {
                "status": "timeout",
                "returncode": -1,
                "stdout": "",
                "stderr": f"Execution timed out after {timeout} seconds."
            }
        except Exception as e:
            logger.error(f"Sandbox execution failed: {e}")
            return {
                "status": "error",
                "returncode": -1,
                "stdout": "",
                "stderr": str(e)
            }
        finally:
            if os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except Exception:
                    pass

code_sandbox = CodeSandbox()
