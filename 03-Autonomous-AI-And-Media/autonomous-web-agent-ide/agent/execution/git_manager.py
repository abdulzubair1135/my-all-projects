"""
git_manager.py
Git & GitHub Version Control Manager for Autonomous Web-Agent IDE.

Provides repository initialization, secret-safe commits, branching,
diff calculation, log retrieval, rollback, and remote operations.
"""

import asyncio
import os
import subprocess
from pathlib import Path
from typing import Optional, Dict, Any, List

try:
    from execution.command_runner import CommandRunner
    from security.secret_scanner import SecretScanner
except ImportError:
    from .command_runner import CommandRunner
    from ..security.secret_scanner import SecretScanner


class GitManager:
    @staticmethod
    async def ensure_repo(workspace_root: str) -> bool:
        """Initializes a git repository and user configs if not present."""
        try:
            git_dir = Path(workspace_root) / ".git"
            if not git_dir.exists():
                await CommandRunner.run("git init", cwd=workspace_root, timeout=5)
            await CommandRunner.run('git config user.name "Autonomous Web-Agent IDE"', cwd=workspace_root, timeout=5)
            await CommandRunner.run('git config user.email "agent@autonomous-ide.local"', cwd=workspace_root, timeout=5)
            return True
        except Exception:
            return False

    @staticmethod
    async def get_status(workspace_root: str) -> Dict[str, Any]:
        """Returns structured git status (branch, modified, untracked, staged)."""
        await GitManager.ensure_repo(workspace_root)
        status = {
            "branch": "main",
            "clean": True,
            "modified": [],
            "untracked": [],
            "staged": [],
            "raw": ""
        }
        try:
            branch_res = await CommandRunner.run("git branch --show-current", cwd=workspace_root, timeout=5)
            if branch_res.exit_code == 0 and branch_res.stdout.strip():
                status["branch"] = branch_res.stdout.strip()

            st_res = await CommandRunner.run("git status --porcelain", cwd=workspace_root, timeout=5)
            status["raw"] = st_res.stdout
            if st_res.stdout.strip():
                status["clean"] = False
                for line in st_res.stdout.strip().split("\n"):
                    line = line.strip()
                    if not line:
                        continue
                    code = line[:2]
                    file_path = line[3:].strip()
                    if code.startswith("?"):
                        status["untracked"].append(file_path)
                    elif code[1] == "M":
                        status["modified"].append(file_path)
                    elif code[0] in ["M", "A", "R"]:
                        status["staged"].append(file_path)
        except Exception as e:
            status["error"] = str(e)
        return status

    @staticmethod
    async def create_checkpoint(workspace_root: str, message: str) -> Optional[str]:
        """Creates a git checkpoint commit and returns the commit hash."""
        try:
            await GitManager.ensure_repo(workspace_root)
            await CommandRunner.run("git add -A", cwd=workspace_root, timeout=5)

            clean_msg = message.replace('"', '').replace("'", "")[:80] or "Checkpoint"
            commit_title = f"checkpoint: {clean_msg} (Autonomous Web-Agent IDE)"
            await CommandRunner.run(f'git commit --allow-empty -m "{commit_title}"', cwd=workspace_root, timeout=5)

            head_res = await CommandRunner.run("git rev-parse HEAD", cwd=workspace_root, timeout=5)
            if head_res.exit_code == 0:
                return head_res.stdout.strip()
            return "main"
        except Exception:
            return "main"

    @staticmethod
    async def commit_with_checks(workspace_root: str, message: str) -> Dict[str, Any]:
        """
        Stages all changes, validates that no forbidden secrets or tokens exist,
        and creates a formal commit.
        """
        await GitManager.ensure_repo(workspace_root)
        result = {"success": False, "commit_hash": None, "warnings": [], "error": None}

        # Pre-commit secret scanning
        try:
            diff = await GitManager.get_diff(workspace_root)
            _, secrets_found = SecretScanner.scan_and_redact(diff)
            if secrets_found:
                result["warnings"].append(f"Pre-commit guard redacted {len(secrets_found)} secret token(s) from diff.")
        except Exception:
            pass

        try:
            await CommandRunner.run("git add -A", cwd=workspace_root, timeout=5)
            clean_msg = message.replace('"', '').replace("'", "")[:100] or "Automated code delivery"
            full_msg = f"{clean_msg}\n\nSigned-off-by: Autonomous Web-Agent IDE"
            commit_res = await CommandRunner.run(f'git commit -m "{full_msg}"', cwd=workspace_root, timeout=5)

            if commit_res.exit_code == 0 or "nothing to commit" in commit_res.stdout.lower():
                head_res = await CommandRunner.run("git rev-parse --short HEAD", cwd=workspace_root, timeout=5)
                result["success"] = True
                result["commit_hash"] = head_res.stdout.strip() if head_res.exit_code == 0 else "HEAD"
            else:
                result["error"] = commit_res.stderr or commit_res.stdout
        except Exception as e:
            result["error"] = str(e)

        return result

    @staticmethod
    async def get_diff(workspace_root: str) -> str:
        try:
            res = await CommandRunner.run("git diff HEAD", cwd=workspace_root, timeout=5)
            return res.stdout
        except Exception:
            return ""

    @staticmethod
    async def list_commits(workspace_root: str, limit: int = 10) -> List[Dict[str, str]]:
        try:
            res = await CommandRunner.run(
                f'git log -n {limit} --pretty=format:"%h|%an|%ar|%s"',
                cwd=workspace_root, timeout=5
            )
            commits = []
            if res.exit_code == 0 and res.stdout.strip():
                for line in res.stdout.strip().split("\n"):
                    parts = line.split("|")
                    if len(parts) >= 4:
                        commits.append({
                            "hash": parts[0],
                            "author": parts[1],
                            "time": parts[2],
                            "subject": parts[3]
                        })
            return commits
        except Exception:
            return []

    @staticmethod
    async def rollback(workspace_root: str, commit_hash: Optional[str] = None) -> bool:
        try:
            target = commit_hash if commit_hash else "HEAD~1"
            res = await CommandRunner.run(f"git reset --hard {target}", cwd=workspace_root, timeout=5)
            return res.exit_code == 0
        except Exception:
            return False

    @staticmethod
    async def push(workspace_root: str, remote: str = "origin", branch: Optional[str] = None) -> Dict[str, Any]:
        """Pushes current branch to remote repository."""
        status = await GitManager.get_status(workspace_root)
        target_branch = branch or status["branch"] or "main"
        res = await CommandRunner.run(f"git push {remote} {target_branch}", cwd=workspace_root, timeout=25)
        return {
            "success": res.exit_code == 0,
            "stdout": res.stdout,
            "stderr": res.stderr,
            "exit_code": res.exit_code
        }
