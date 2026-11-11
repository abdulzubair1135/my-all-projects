import argparse
import asyncio
import os
import sys
import json
from pathlib import Path

# Force UTF-8 stdout/stderr on Windows to avoid 'charmap' codec errors
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

# Add agent directory to sys.path for absolute imports
AGENT_ROOT = Path(__file__).resolve().parent
if str(AGENT_ROOT) not in sys.path:
    sys.path.insert(0, str(AGENT_ROOT))

from dotenv import load_dotenv
load_dotenv()

from browser.providers.mock_provider import MockLocalProvider
from browser.providers.deepseek_web import DeepSeekWebProvider
from browser.providers.generic_web import GenericWebProvider
from browser.providers.gemini_web import GeminiWebProvider
from browser.providers.smart_provider import SmartProvider
from browser.providers.nemotron_hf import NemotronHuggingFaceProvider
from core.orchestrator import Orchestrator
from multiagent.team_orchestrator import MultiAgentTeamOrchestrator

def get_provider(name: str, headless: bool = False):
    if name in ["smart", "smart_cognitive", "cognitive", "auto"]:
        return SmartProvider(headless=headless)
    elif name in ["nemotron", "nemotron_hf", "huggingface", "nvidia"]:
        return NemotronHuggingFaceProvider()
    elif name == "gemini_web":
        return GeminiWebProvider(headless=headless)
    elif name in ["chatgpt_web", "generic_web"]:
        return GenericWebProvider(headless=headless)
    elif name == "deepseek_web":
        return DeepSeekWebProvider(headless=headless)
    elif name == "mock_provider":
        return MockLocalProvider()
    else:
        return SmartProvider(headless=headless)

async def main() -> int:
    parser = argparse.ArgumentParser(description="Autonomous Multi-Agent Web-Agent IDE")
    parser.add_argument("--project-id", required=True, help="Project ID")
    parser.add_argument("--run-id", required=True, help="Agent Run ID")
    parser.add_argument("--project-path", required=True, help="Path to project workspace")
    parser.add_argument("--prompt", required=True, help="User project prompt / requirement")
    parser.add_argument("--provider", default="deepseek_web", help="LLM Provider (deepseek_web, generic_web, mock_provider)")
    parser.add_argument("--approval-mode", default="AUTO", help="Approval Mode (AUTO, SAFE, ASK)")
    parser.add_argument("--mode", default="multiagent", help="Execution Mode (multiagent, single)")
    parser.add_argument("--db-path", default=None, help="Path to SQLite database")
    parser.add_argument("--images", default="", help="Comma-separated image file paths to attach to prompt")

    args = parser.parse_args()

    db_path = args.db_path or os.getenv("DATABASE_PATH", str(AGENT_ROOT.parent / "data" / "agent.sqlite"))
    headless = os.getenv("BROWSER_HEADLESS", "false").lower() == "true"

    # Parse image paths
    image_paths = [p.strip() for p in args.images.split(",") if p.strip()] if args.images else []

    provider = get_provider(args.provider, headless=headless)
    await provider.connect()

    if args.mode == "multiagent":
        orchestrator = MultiAgentTeamOrchestrator(
            project_id=args.project_id,
            run_id=args.run_id,
            workspace_root=args.project_path,
            provider=provider,
            db_path=db_path,
            approval_mode=args.approval_mode,
            images=image_paths,
        )
    else:
        orchestrator = Orchestrator(
            project_id=args.project_id,
            run_id=args.run_id,
            workspace_root=args.project_path,
            provider=provider,
            db_path=db_path,
            approval_mode=args.approval_mode
        )

    try:
        success = await orchestrator.run(args.prompt)
        return 0 if success else 1
    finally:
        await provider.close()

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
