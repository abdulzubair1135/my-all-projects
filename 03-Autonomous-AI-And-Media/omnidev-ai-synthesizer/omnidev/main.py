import sys
import os
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table

import config
from core.orchestrator import Orchestrator

from config import console

def print_welcome_banner():
    banner = """
  ██████╗ ███╗   ███╗███╗   ██╗██╗██████╗ ███████╗██╗   ██╗
 ██╔═══██╗████╗ ████║████╗  ██║██║██╔══██╗██╔════╝██║   ██║
 ██║   ██║██╔████╔██║██╔██╗ ██║██║██║  ██║█████╗  ██║   ██║
 ██║   ██║██║╚██╔╝██║██║╚██╗██║██║██║  ██║██╔══╝  ╚██╗ ██╔╝
 ╚██████╔╝██║ ╚═╝ ██║██║ ╚████║██║██████╔╝███████╗ ╚████╔╝ 
  ╚═════╝ ╚═╝     ╚═╝╚═╝  ╚═══╝╚═╝╚═════╝ ╚══════╝  ╚═══╝  
    Autonomous Multi-Modal Development Agent (Chrome + Terminal + Self-Healing)
    """
    console.print(f"[bold cyan]{banner}[/bold cyan]")
    
    table = Table(title="Quick Command Guide", border_style="dim")
    table.add_column("Command / Action", style="bold green")
    table.add_column("Example", style="white")
    table.add_row("Build CRUD App", "build app Library management system with book issue/return")
    table.add_row("Build Website", "build website Portfolio for AI Engineer with dark mode")
    table.add_row("Generate PPT", "build ppt Future of Artificial Intelligence 6 slides")
    table.add_row("Generate Image", "build img Cyberpunk laboratory with holograms")
    table.add_row("Modify Codebase", "modify add author search filter to books API")
    table.add_row("Run Terminal", "run python --version  OR  run pip list")
    table.add_row("Exit", "exit  or  quit")
    console.print(table)
    console.print()

def get_clipboard_text() -> str:
    """Safely retrieves text from Windows clipboard using user32 / ctypes."""
    if sys.platform != "win32":
        return ""
    try:
        import ctypes
        from ctypes import wintypes
        user32 = ctypes.windll.user32
        kernel32 = ctypes.windll.kernel32
        if not user32.OpenClipboard(None):
            return ""
        try:
            CF_UNICODETEXT = 13
            h_clip = user32.GetClipboardData(CF_UNICODETEXT)
            if not h_clip:
                return ""
            kernel32.GlobalLock.restype = ctypes.c_wchar_p
            text_ptr = kernel32.GlobalLock(h_clip)
            if not text_ptr:
                return ""
            text = str(text_ptr)
            kernel32.GlobalUnlock(h_clip)
            return text
        finally:
            user32.CloseClipboard()
    except Exception:
        return ""

def get_user_input() -> str:
    """
    Reads user input with automatic multi-line paste support on Windows.
    Captures full error tracebacks, logs, and multi-line commands cleanly.
    """
    first_line = Prompt.ask("\n[bold cyan]OmniDev AI[/bold cyan] [bold green]❯[/bold green]")
    if not first_line:
        return ""
    
    first_clean = first_line.strip()
    
    # If user types 'paste' or 'clipboard', pull full clipboard content
    if first_clean.lower() in ["paste", "clip", "clipboard", "error"]:
        clip = get_clipboard_text()
        if clip and len(clip.strip()) > 5:
            console.print(f"[dim cyan]📋 Loaded {len(clip.splitlines())} lines from Windows Clipboard[/dim cyan]")
            return clip.strip()

    lines = [first_line]
    if sys.platform == "win32":
        try:
            import msvcrt
            import time
            # Multi-line paste debounce drainer: drains all buffered keystrokes
            time.sleep(0.12)
            buf = []
            while True:
                hit = False
                while msvcrt.kbhit():
                    hit = True
                    try:
                        c = msvcrt.getwch()
                        if c == '\r':
                            c = '\n'
                        buf.append(c)
                    except Exception:
                        break
                if hit:
                    time.sleep(0.08)
                else:
                    break
            
            if buf:
                extra_text = "".join(buf)
                for extra_line in extra_text.splitlines():
                    if extra_line.strip():
                        lines.append(extra_line)
        except Exception:
            pass
    
    full_text = "\n".join(lines).strip()
    
    # If first line looks like part of a Godot error or traceback, check if clipboard has the rest
    if any(k in full_text for k in ["SCRIPT ERROR:", "Parse Error:", "at: WorldGenerator", "at: Player", "at: Animal", "Traceback (most recent call last)"]):
        clip = get_clipboard_text()
        if clip and len(clip) > len(full_text) and (full_text.splitlines()[0] in clip or "SCRIPT ERROR:" in clip):
            console.print(f"[dim cyan]✓ Auto-completed full error traceback from Clipboard ({len(clip.splitlines())} lines)[/dim cyan]")
            return clip.strip()
            
    if len(lines) > 1:
        console.print(f"[dim cyan]✓ Captured full multi-line paste ({len(lines)} lines)[/dim cyan]")
    return full_text

def main():
    print_welcome_banner()

    # Check if help requested
    if len(sys.argv) > 1 and sys.argv[1].lower() in ["--help", "-h", "help"]:
        return

    orchestrator = Orchestrator(config.WORKSPACE_DIR)

    # Check if command passed via CLI arguments
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
        console.print(f"[bold yellow]Executing requested task:[/bold yellow] {query}")
        res = orchestrator.process_user_request(query)
        if isinstance(res, dict) and res.get("app_url") and orchestrator.process_manager.active_processes:
            console.print(f"\n[bold green]🚀 Server is running at: {res['app_url']}[/bold green]")
            console.print("[yellow]Press Ctrl+C to stop the server...[/yellow]")
            try:
                import time
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                orchestrator.process_manager.stop_all()
        return

    # Interactive REPL Loop
    while True:
        try:
            user_input = get_user_input()
            if not user_input.strip():
                continue

            if user_input.strip().lower() in ["exit", "quit", "q"]:
                console.print("[yellow]Shutting down background services...[/yellow]")
                orchestrator.process_manager.stop_all()
                console.print("[bold green]Goodbye![/bold green]")
                break

            if user_input.strip().lower() == "help":
                print_welcome_banner()
                continue

            orchestrator.process_user_request(user_input)

        except KeyboardInterrupt:
            console.print("\n[yellow]Interrupted. Cleaning up...[/yellow]")
            orchestrator.process_manager.stop_all()
            break
        except Exception as e:
            console.print(f"[bold red]An error occurred:[/bold red] {e}")

if __name__ == "__main__":
    main()
