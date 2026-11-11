import re
from pathlib import Path
from typing import Dict, Any, Optional, List, Callable
from config import console
from tools.file_manager import FileManager
from tools.knowledge_base import ErrorKnowledgeBase

class AutoHealer:
    """
    Self-healing loop:
    Catches errors (tracebacks, test failures), consults autonomous memory first,
    then AI brain, applies code fixes, caches successful solutions, and re-executes.
    """
    def __init__(self, brain, file_manager, max_retries: int = 10):
        self.brain = brain
        self.file_manager = file_manager
        self.max_retries = max_retries
        self.kb = ErrorKnowledgeBase()

    def extract_referenced_files(self, error_text: str) -> List[str]:
        """
        Extracts filenames referenced in Python tracebacks or Node errors.
        """
        files = set()
        # Python traceback pattern: File "...", line X
        py_matches = re.findall(r'File "([^"]+)", line \d+', error_text)
        for m in py_matches:
            p = Path(m)
            # Only track local workspace files, ignore python standard lib or venv
            if ".venv" not in m and "Python3" not in m and "lib" not in m.lower():
                files.add(p.name)

        # Node / general pattern: at ... (path/file.js:X:Y)
        js_matches = re.findall(r'([a-zA-Z0-9_\-\./\\]+\.(?:py|js|ts|html|css)):(?:\d+)', error_text)
        for m in js_matches:
            if "node_modules" not in m:
                files.add(Path(m).name)

        return list(files)

    def heal(
        self,
        command: str,
        error_output: str,
        workspace_dir: Path,
        verify_callback: Callable[[], bool],
        extra_context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Executes the self-healing retry loop.
        verify_callback is a function that returns True if the fix worked.
        """
        console.print(f"[bold yellow]⚠️ Auto-Healer activated for command:[/bold yellow] [cyan]{command}[/cyan]")
        
        # Step 0: Try Instant Local Fix from Knowledge Base / Memory without calling DeepSeek
        local_fix = self.kb.try_local_auto_fix(error_output, workspace_dir)
        if local_fix:
            console.print(f"[bold green]⚡ Applied Instant Local Fix: {local_fix}[/bold green]")
            try:
                if verify_callback():
                    console.print(f"[bold green]🎉 Problem auto-healed locally in 0.1s without needing DeepSeek![/bold green]")
                    return {
                        "success": True,
                        "attempts": 0,
                        "local_fix": local_fix,
                        "history": [{"attempt": 0, "fix": local_fix}]
                    }
            except Exception as e:
                error_output = str(e)

        attempt = 0
        history = []

        while attempt < self.max_retries:
            attempt += 1
            console.print(f"[bold cyan]🔄 Healing Attempt {attempt}/{self.max_retries}...[/bold cyan]")

            # 1. Identify files involved
            referenced_filenames = self.extract_referenced_files(error_output)
            files_context = []
            
            # Find and read matching files in app workspace
            local_file_mgr = FileManager(workspace_dir)
            all_files = local_file_mgr.list_files()
            for af in all_files:
                if af.name in referenced_filenames or len(referenced_filenames) == 0:
                    try:
                        content = local_file_mgr.read_file(af)
                        # Avoid sending huge files
                        if len(content) < 25000:
                            files_context.append(f"--- FILE: {af.name} ---\n{content}\n")
                    except Exception:
                        pass
                if len(files_context) >= 3:
                    break

            context_str = "\n".join(files_context)
            
            file_tree = [f.name for f in all_files if not f.name.startswith(".")]
            tree_str = ", ".join(file_tree)
            
            # 2. Build Prompt for DeepSeek / Gemini
            prompt = (
                f"You are OmniDev AI Auto-Debugger. A runtime error occurred while executing a command.\n\n"
                f"COMMAND: {command}\n"
                f"ERROR TRACEBACK / OUTPUT:\n{error_output}\n\n"
                f"PROJECT STRUCTURE: [{tree_str}]\n\n"
            )
            if extra_context:
                prompt += f"ORIGINAL INTENT & CONTEXT:\n{extra_context}\n\n"
            if context_str:
                prompt += f"RELEVANT CODE FILES:\n{context_str}\n\n"

            prompt += (
                "TASK:\n"
                "1. Analyze why this error happened.\n"
                "2. Provide the complete fixed code for the broken file.\n"
                "3. IMPORTANT: Maintain the core application logic, styling, and endpoints.\n"
                "4. Use this format strictly:\n"
                "FILE: <filename>\n"
                "```<language>\n"
                "<complete code for this file>\n"
                "```\n"
            )

            # 3. Ask AI Brain in the SAME active chat (no new chat, attach file if available)
            console.print("[magenta]🤖 Asking DeepSeek/Gemini for solution (in active chat)...[/magenta]")
            attach_file = (workspace_dir / "main.py") if (workspace_dir / "main.py").exists() else None
            ai_response = self.brain.ask(prompt, new_chat=False, file_to_attach=attach_file)

            # 4. Parse AI Response and Apply Fix
            files_updated = self._apply_ai_code_blocks(ai_response, workspace_dir)
            
            # If no files were matched, try fallback aggressive parsing
            if not files_updated:
                console.print("[yellow]⚠️ No 'FILE:' tag found. Searching for raw runnable code blocks...[/yellow]")
                code_blocks = re.findall(r"```(?:[a-zA-Z0-9_\-]+)?\n(.*?)```", ai_response, re.DOTALL)
                if code_blocks:
                    main_py = workspace_dir / "main.py"
                    clean_code = self._sanitize_code("main.py", code_blocks[0].strip())
                    local_file_mgr.write_file(main_py, clean_code)
                    files_updated.append("main.py")

            history.append({
                "attempt": attempt,
                "error": error_output[:300],
                "files_updated": files_updated
            })

            console.print(f"[green]✓ Applied fixes to: {files_updated}[/green]")
            console.print("[yellow]Verifying fix...[/yellow]")

            # 5. Verify using callback
            try:
                is_resolved = verify_callback()
                if is_resolved:
                    console.print(f"[bold green]🎉 Problem successfully auto-healed in attempt {attempt}![/bold green]")
                    # Record solution to Autonomous Memory so it's learned forever!
                    self.kb.record_successful_fix(error_output, files_updated, workspace_dir)
                    return {
                        "success": True,
                        "attempts": attempt,
                        "history": history
                    }
            except Exception as e:
                error_output = str(e)

        console.print(f"[bold red]❌ Could not auto-heal after {self.max_retries} attempts.[/bold red]")
        return {
            "success": False,
            "attempts": attempt,
            "history": history
        }

    @staticmethod
    def _sanitize_code(rel_path: str, code: str) -> str:
        if rel_path.endswith(".py"):
            def fix_open(m):
                args = m.group(1)
                if "encoding" in args or "wb" in args or "rb" in args:
                    return m.group(0)
                if re.search(r'["\']r["\']', args):
                    return f'open({args}, encoding="utf-8")'
                if "," not in args:
                    return f'open({args}, "r", encoding="utf-8")'
                return f'open({args}, encoding="utf-8")'

            code = re.sub(r'\bopen\(([^)]+)\)', fix_open, code)
        return code

    def _apply_ai_code_blocks(self, ai_text: str, workspace_dir: Path) -> List[str]:
        """
        Parses FILE: <name> and code blocks from AI response and writes them to disk.
        """
        updated_files = []
        file_mgr = FileManager(workspace_dir)

        # Pattern matching FILE: filename followed by ```lang ... ```
        p1 = r"(?:FILE|File|file):\s*`?([a-zA-Z0-9_\-\./\\]+\.[a-zA-Z0-9]+)`?\s*```(?:[a-zA-Z0-9_\-]+)?\n(.*?)```"
        matches = re.findall(p1, ai_text, re.DOTALL)

        if not matches:
            # Fallback: check for any markdown code blocks
            code_blocks = re.findall(r"```(?:[a-zA-Z0-9_\-]+)?\n(.*?)```", ai_text, re.DOTALL)
            if code_blocks:
                main_py = workspace_dir / "main.py"
                clean_code = self._sanitize_code("main.py", code_blocks[0].strip())
                file_mgr.write_file(main_py, clean_code)
                updated_files.append("main.py")
            return updated_files

        seen = set()
        for file_rel_path, code in matches:
            clean_rel = file_rel_path.strip().strip("`* ").replace("\\", "/")
            # Sanitize: Strip any noise like pythonCopyDownload or CopyDownload
            clean_rel = re.sub(r'(?:python)?CopyDownload.*$', '', clean_rel, flags=re.IGNORECASE)
            valid_match = re.search(r'([a-zA-Z0-9_\-\./]+\.(?:py|html|css|js|ts|json|bat|txt|md|sql))\b', clean_rel)
            if valid_match:
                clean_rel = valid_match.group(1)

            if clean_rel in seen:
                continue
            seen.add(clean_rel)
            clean_code = self._sanitize_code(clean_rel, code.strip())
            dest = workspace_dir / clean_rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            file_mgr.write_file(dest, clean_code)
            updated_files.append(clean_rel)

            # Duplicate index.html to both root and static/
            if clean_rel == "index.html" and "static/index.html" not in seen:
                file_mgr.write_file(workspace_dir / "static" / "index.html", clean_code)
            elif clean_rel == "static/index.html" and "index.html" not in seen:
                file_mgr.write_file(workspace_dir / "index.html", clean_code)

        return updated_files
