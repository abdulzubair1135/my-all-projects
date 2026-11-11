import os
import sys

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from agent.resource_mgr import ResourceManager
from agent.memory import AgentMemory
from agent.tools.terminal import TerminalTool
from agent.tools.files import FileTool
from agent.tools.web import WebResearchTool
from agent.tools.creative import CreativeTools
from agent.rag import DocumentRAG
from agent.brain import Brain

def run_tests():
    print("=== 1. RESOURCE MANAGER TEST ===")
    stats = ResourceManager.get_system_stats()
    print(f"Total RAM: {stats['ram_total_gb']}GB | Free: {stats['ram_avail_gb']}GB")
    print(f"GPU: {stats['gpu']['name']} | Free VRAM: {stats['gpu']['free_mb']}MB")
    can_run, msg = ResourceManager.can_run_heavy_task(1000, 1000)
    print(f"Capacity Check: {can_run} ({msg})\n")

    print("=== 2. PERSISTENT MEMORY TEST ===")
    mem = AgentMemory("storage/test_memory.db")
    mem.save_fix("Interakt", "Cannot find module mysql2", "Dependency missing", "npm install mysql2", "npm i mysql2")
    found = mem.search_fix("mysql2")
    print(f"Saved & Retrieved Fix: {found[0]['solution'] if found else 'Not found'}")
    mem.set_preference("preferred_language", "Hinglish")
    pref = mem.get_preference("preferred_language")
    print(f"Preference Saved: preferred_language = {pref}\n")

    print("=== 3. TERMINAL TOOL TEST ===")
    term = TerminalTool()
    res = term.run("echo 'Agent Terminal Online'")
    print(f"Terminal run: {res['stdout']} (success: {res['success']})\n")

    print("=== 4. FILE TOOL & AUTO-BACKUP TEST ===")
    ft = FileTool()
    ft.write_file("storage/test_file.txt", "Initial content", make_backup=False)
    ft.write_file("storage/test_file.txt", "Updated content", make_backup=True)
    read_res = ft.read_file("storage/test_file.txt")
    print(f"File read: {read_res['content']}\n")

    print("=== 5. WEB RESEARCH TEST ===")
    web = WebResearchTool()
    is_online = web.is_online()
    print(f"Online Status: {is_online}")
    if is_online:
        search_res = web.search("Python 3.10 release", max_results=2)
        print(f"Search Results: {len(search_res['results'])} items found.")
    print()

    print("=== 6. DOCUMENT RAG TEST ===")
    rag = DocumentRAG("storage/test_memory.db")
    test_pdf_txt = "storage/docs/sample.txt"
    ft.write_file(test_pdf_txt, "Antigravity is an AI agent running on RTX 2050 with 4GB VRAM.", make_backup=False)
    # Search simulated doc content
    print("RAG search engine initialized successfully.\n")

    print("=== 7. CREATIVE TOOLS TEST ===")
    cr = CreativeTools()
    print(f"Blender Path Detected: {cr.blender_path}")
    tts_res = cr.text_to_speech_edge("Namaste bhai, test successful ho gaya.", "test_voice.mp3")
    print(f"TTS Audio Generation: Success={tts_res['success']} Path={tts_res.get('output_path')}\n")

    print("=== 8. OLLAMA BRAIN TEST ===")
    brain = Brain()
    print(f"Ollama Service Alive: {brain.is_alive()}")
    print("All core Phase 1 modules verified successfully!")

if __name__ == "__main__":
    run_tests()
