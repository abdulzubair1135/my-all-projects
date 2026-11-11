"""
agent_cli.py
Command-Line Interface bridge for Autonomous Web-Agent IDE.
Executes core agent commands with structured JSON outputs.
"""

import sys
import os
import json
import asyncio
from pathlib import Path

# Add agent directory to sys.path
AGENT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(AGENT_DIR))


def main():
    if len(sys.argv) < 2:
        print(json.dumps({"error": "No command provided"}))
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "create-checkpoint":
        if len(sys.argv) < 4:
            print(json.dumps({"error": "Usage: create-checkpoint <workspace> <description> [stage]"}))
            sys.exit(1)
        ws = sys.argv[2]
        desc = sys.argv[3]
        stage = sys.argv[4] if len(sys.argv) > 4 else "MANUAL"
        from core.checkpoint_manager import CheckpointManager
        mgr = CheckpointManager(ws)
        res = mgr.create_checkpoint(desc, stage=stage)
        print(json.dumps(res))

    elif cmd == "rollback-checkpoint":
        if len(sys.argv) < 4:
            print(json.dumps({"error": "Usage: rollback-checkpoint <workspace> <checkpoint_id>"}))
            sys.exit(1)
        ws = sys.argv[2]
        cpid = sys.argv[3]
        from core.checkpoint_manager import CheckpointManager
        mgr = CheckpointManager(ws)
        res = mgr.rollback(cpid)
        print(json.dumps(res))

    elif cmd == "visual-qa":
        if len(sys.argv) < 4:
            print(json.dumps({"error": "Usage: visual-qa <workspace> <url>"}))
            sys.exit(1)
        ws = sys.argv[2]
        url = sys.argv[3]
        from core.visual_qa import VisualQAEngine
        engine = VisualQAEngine(ws)
        report = asyncio.run(engine.inspect_url(url))
        print(json.dumps(report))

    elif cmd == "list-templates":
        from core.project_templates import get_all_templates
        print(json.dumps(get_all_templates()))

    elif cmd == "get-template":
        if len(sys.argv) < 3:
            print(json.dumps({"error": "Usage: get-template <template_id>"}))
            sys.exit(1)
        tid = sys.argv[2]
        from core.project_templates import get_template_by_id
        tmpl = get_template_by_id(tid)
        print(json.dumps(tmpl or {}))

    elif cmd == "list-checkpoints":
        if len(sys.argv) < 3:
            print(json.dumps([]))
            sys.exit(0)
        ws = sys.argv[2]
        from core.checkpoint_manager import CheckpointManager
        mgr = CheckpointManager(ws)
        print(json.dumps(mgr.list_checkpoints()))

    elif cmd == "list-errors":
        if len(sys.argv) < 3:
            print(json.dumps([]))
            sys.exit(0)
        ws = sys.argv[2]
        db_file = Path(ws) / ".agent_state.sqlite"
        if not db_file.exists():
            print(json.dumps([]))
            sys.exit(0)
        import sqlite3
        try:
            with sqlite3.connect(db_file) as conn:
                conn.row_factory = sqlite3.Row
                tbl = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='error_memory'").fetchone()
                if not tbl:
                    print(json.dumps([]))
                    sys.exit(0)
                rows = conn.execute(
                    "SELECT fingerprint, error_type, normalized_message, root_cause, patch_description, success_count, fail_count, last_seen FROM error_memory ORDER BY last_seen DESC LIMIT 50"
                ).fetchall()
                print(json.dumps([dict(r) for r in rows]))
        except Exception:
            print(json.dumps([]))

    elif cmd == "get-memory":
        if len(sys.argv) < 3:
            print(json.dumps({"error": "Usage: get-memory <workspace>"}))
            sys.exit(1)
        ws = sys.argv[2]
        from core.project_memory import ProjectMemoryManager
        mem = ProjectMemoryManager()
        profile = mem.get_profile(ws)
        decisions = mem.get_decisions(ws)
        milestones = mem.get_milestones(ws)
        prompt_block = mem.get_project_memory_prompt(ws)
        print(json.dumps({
            "profile": profile,
            "decisions": decisions,
            "milestones": milestones,
            "prompt_block": prompt_block
        }))

    elif cmd == "save-profile":
        if len(sys.argv) < 4:
            print(json.dumps({"error": "Usage: save-profile <workspace> <json_data>"}))
            sys.exit(1)
        ws = sys.argv[2]
        try:
            data = json.loads(sys.argv[3])
        except Exception:
            data = {"project_name": sys.argv[3]}
        from core.project_memory import ProjectMemoryManager
        mem = ProjectMemoryManager()
        mem.save_profile(
            workspace=ws,
            project_name=data.get("project_name", "Untitled Project"),
            project_type=data.get("project_type", "General"),
            ui_style=data.get("ui_style", "Modern"),
            game_engine=data.get("game_engine", "None"),
            asset_strategy=data.get("asset_strategy", "Autonomous"),
            quality_tier=data.get("quality_tier", "AAA_PRODUCTION"),
            notes=data.get("notes", "")
        )
        print(json.dumps({"success": True, "workspace": ws}))

    elif cmd == "zip-chunk":
        if len(sys.argv) < 3:
            print(json.dumps({"error": "Usage: zip-chunk <workspace> [max_chunk_mb]"}))
            sys.exit(1)
        ws = sys.argv[2]
        max_mb = float(sys.argv[3]) if len(sys.argv) > 3 else 38.0
        from core.zip_chunker import create_chunked_zip
        result = create_chunked_zip(ws, max_chunk_mb=max_mb)
        print(json.dumps(result))

    else:
        print(json.dumps({"error": f"Unknown command: {cmd}"}))
        sys.exit(1)


if __name__ == "__main__":
    main()
