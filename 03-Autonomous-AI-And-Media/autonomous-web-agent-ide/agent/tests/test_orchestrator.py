import pytest
import tempfile
import asyncio
import os
import sqlite3
from pathlib import Path
from agent.browser.providers.mock_provider import MockLocalProvider
from agent.core.orchestrator import Orchestrator

@pytest.mark.asyncio
async def test_full_orchestrator_autonomous_loop():
    with tempfile.TemporaryDirectory() as tmp_workspace:
        with tempfile.TemporaryDirectory() as tmp_db_dir:
            db_path = str(Path(tmp_db_dir) / "test.sqlite")

            # Initialize SQLite tables in test DB
            conn = sqlite3.connect(db_path)
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS tasks (
                  id TEXT PRIMARY KEY,
                  project_id TEXT,
                  run_id TEXT,
                  title TEXT,
                  description TEXT,
                  status TEXT,
                  order_index INTEGER,
                  retry_count INTEGER,
                  error_message TEXT,
                  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                );
                CREATE TABLE IF NOT EXISTS task_dependencies (
                  id TEXT PRIMARY KEY,
                  task_id TEXT,
                  depends_on_task_id TEXT
                );
                CREATE TABLE IF NOT EXISTS commands (
                  id TEXT PRIMARY KEY,
                  project_id TEXT,
                  run_id TEXT,
                  task_id TEXT,
                  command TEXT,
                  cwd TEXT,
                  exit_code INTEGER,
                  duration_ms INTEGER,
                  stdout TEXT,
                  stderr TEXT,
                  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                );
                CREATE TABLE IF NOT EXISTS approvals (
                  id TEXT PRIMARY KEY,
                  project_id TEXT,
                  run_id TEXT,
                  action_type TEXT,
                  action_payload TEXT,
                  status TEXT,
                  reason TEXT,
                  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                );
            """)
            conn.close()

            provider = MockLocalProvider()
            orchestrator = Orchestrator(
                project_id="test_proj_1",
                run_id="run_1",
                workspace_root=tmp_workspace,
                provider=provider,
                db_path=db_path,
                approval_mode="AUTO"
            )

            try:
                success = await orchestrator.run("Build me an expense management app")
                assert success is True

                # Verify files were created in sandbox
                assert (Path(tmp_workspace) / "server" / "package.json").exists() or (Path(tmp_workspace) / "package.json").exists()
                assert (Path(tmp_workspace) / "server" / "server.js").exists() or (Path(tmp_workspace) / "src" / "App.jsx").exists()
            finally:
                orchestrator.state_mgr.close()
