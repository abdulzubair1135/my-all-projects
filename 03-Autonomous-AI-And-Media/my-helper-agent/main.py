import sys
import os

# Ensure UTF-8 output in Windows PowerShell / CMD
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from agent.autonomous_agent import AutonomousAgent
from agent.resource_mgr import ResourceManager

def banner():
    stats = ResourceManager.get_system_stats()
    gpu = stats["gpu"]
    print("=" * 65)
    print("  PERSONAL AUTONOMOUS AI AGENT (QWEN 3.5 4B TOOL-CALLING)")
    print("=" * 65)
    print(f"  System: Ryzen 7 7435HS | RAM: {stats['ram_avail_gb']}GB free / {stats['ram_total_gb']}GB")
    print(f"  GPU:    {gpu['name']} ({gpu['free_mb']}MB free VRAM)")
    print("  Brain:  Ollama Qwen3.5:4B (Native Tool Calling & Execution)")
    print("=" * 65)
    print("  Type your prompt in Hinglish/English (or 'exit' to quit).\n")

def main():
    banner()
    agent = AutonomousAgent()

    while True:
        try:
            user_input = input("User >> ").strip()
            if not user_input:
                continue
            if user_input.lower() in ["exit", "quit", "bye", "band kar"]:
                print("\nAlvida bhai! Models unload kar raha hoon...")
                ResourceManager.unload_ollama_model("qwen3.5:4b")
                break

            response = agent.chat(user_input)
            print(f"\nAgent >> {response}\n")
            print("-" * 65)

        except KeyboardInterrupt:
            print("\nExiting...")
            ResourceManager.unload_ollama_model("qwen3.5:4b")
            break
        except Exception as e:
            print(f"\nAgent Error >> {e}\n")

if __name__ == "__main__":
    main()
