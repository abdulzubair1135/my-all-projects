import sys
import unittest
import tempfile
import shutil
import sqlite3
from pathlib import Path

OMNIDEV_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(OMNIDEV_DIR))

from core.orchestrator import Orchestrator
from core.state_machine import AutonomousFSM, FSMState
from core.task_graph import TaskGraph, Task, TaskStatus
from core.command_guard import CommandGuard
from core.permission_manager import PermissionManager
from core.memory_vault import MemoryVault
from core.error_memory import ErrorMemory
from core.project_graph import ProjectKnowledgeGraph
from core.event_bus import event_bus
from tools.env_doctor import EnvironmentDoctor
from tools.db_tool import DatabaseTool
from tools.dep_intelligence import DependencyIntelligence
from tools.security_scanner import SecurityScanner
from tools.browser_tool import BrowserTool
from tools.adb_tool import ADBTool
from tools.git_tool import GitTool
from builders.android_builder import AndroidAppBuilder
from builders.game_builder import GameBuilder
from builders.doc_builder import DocumentBuilder

class MockBrain:
    def ask(self, prompt, **kwargs):
        if "Android" in prompt or "android" in prompt.lower():
            return "FILE: app/src/main/java/MainActivity.java\n```java\npackage com.example.app;\npublic class MainActivity {}\n```"
        if "game" in prompt.lower() or "canvas" in prompt.lower():
            return "FILE: index.html\n```html\n<!DOCTYPE html><html><head><title>Arcade Game</title></head><body><canvas id='c'></canvas><script>console.log('Game loaded');</script></body></html>\n```"
        if "report" in prompt.lower() or "document" in prompt.lower():
            return "# Technical Report\n\n## Executive Summary\nAll systems operational."
        return "FILE: main.py\n```python\nprint('OmniDev Live Test')\n```"

class TestOmniDevMasterVerification(unittest.TestCase):
    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp())
        self.mock_brain = MockBrain()

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_01_fsm_and_task_dag(self):
        """Verify 40-state FSM transitions and Task DAG execution"""
        fsm = AutonomousFSM(FSMState.IDLE)
        fsm.transition_to(FSMState.UNDERSTAND, "Testing understand")
        fsm.transition_to(FSMState.PLAN, "Testing plan")
        fsm.transition_to(FSMState.IMPLEMENT, "Testing implement")
        fsm.transition_to(FSMState.SUCCESS, "Testing success")
        self.assertEqual(fsm.current_state, FSMState.SUCCESS)

        dag = TaskGraph()
        t1 = Task(title="Task 1", assigned_agent="Architect")
        t2 = Task(title="Task 2", assigned_agent="Coder", dependencies=[t1.task_id])
        dag.add_task(t1)
        dag.add_task(t2)
        self.assertFalse(dag.detect_cycles())
        
        ready = dag.get_ready_tasks()
        self.assertEqual(len(ready), 1)
        dag.mark_completed(t1.task_id)
        ready2 = dag.get_ready_tasks()
        self.assertEqual(ready2[0].task_id, t2.task_id)

    def test_02_command_guard_and_permissions(self):
        """Verify safety guard blocks dangerous commands and redacts secrets"""
        is_safe, _ = CommandGuard.check_command_safety("format C:")
        self.assertFalse(is_safe)
        
        is_safe, _ = CommandGuard.check_command_safety("git push origin main --force")
        self.assertFalse(is_safe)

        # Sandbox check
        valid, _, _ = CommandGuard.validate_path_sandbox(Path("../../escape.py"), self.temp_dir)
        self.assertFalse(valid)

        # Secret redaction
        sample = "sk-99887766554433221100aabbccdd is secret key"
        redacted = CommandGuard.redact_secrets(sample)
        self.assertNotIn("sk-998877665544", redacted)

    def test_03_memory_vault_and_error_fingerprint(self):
        """Verify SQLite memory vault & error fingerprint indexing"""
        vault_db = self.temp_dir / "test_mem.db"
        vault = MemoryVault(vault_db)
        vault.record_mission("m_100", "Test goal", "COMPLETED", {"files": 5})

        err_mem = ErrorMemory(vault)
        trace = 'File "server.py", line 10, in <module>\nIndexError: list index out of range'
        fp = err_mem.generate_fingerprint(trace)
        self.assertTrue(len(fp) > 0)
        err_mem.record_solution(trace, "Handled empty list", "if items: return items[0]", success=True)
        sol = err_mem.lookup_solution(trace)
        self.assertIsNotNone(sol)
        self.assertEqual(sol["solution_patch"], "if items: return items[0]")

    def test_04_environment_doctor(self):
        """Verify toolchain and system diagnostic scan"""
        diag = EnvironmentDoctor.diagnose()
        self.assertTrue(diag["success"])
        self.assertIn("python", diag["tools"])
        self.assertTrue(diag["tools"]["python"]["installed"])

    def test_05_database_tool(self):
        """Verify SQLite database inspection and query runner"""
        db_path = self.temp_dir / "app.db"
        conn = sqlite3.connect(str(db_path))
        conn.execute("CREATE TABLE products (id INT, title TEXT)")
        conn.execute("INSERT INTO products VALUES (1, 'OmniDev Pro')")
        conn.commit()
        conn.close()

        schema = DatabaseTool.inspect_sqlite_schema(db_path)
        self.assertIn("products", schema["tables"])
        res = DatabaseTool.run_safe_query(db_path, "SELECT * FROM products")
        self.assertEqual(res["rows"][0]["title"], "OmniDev Pro")

    def test_06_security_scanner(self):
        """Verify vulnerability & secret scanner"""
        p = self.temp_dir / "config.env"
        p.write_text("API_SECRET = 'ghp_your_personal_access_token_here'", encoding="utf-8")
        scanner = SecurityScanner(self.temp_dir)
        audit = scanner.full_audit()
        self.assertFalse(audit["clean"])
        self.assertIn("config.env", audit["secret_leaks"])

    def test_07_ast_knowledge_graph_nl_search(self):
        """Verify AST parsing and natural language search"""
        code = self.temp_dir / "billing.py"
        code.write_text("""
class PaymentProcessor:
    def process_invoice(self, amount):
        return True
""", encoding="utf-8")
        graph = ProjectKnowledgeGraph(self.temp_dir)
        matches = graph.search_code_nl("Payment processor invoice billing")
        self.assertTrue(len(matches) > 0)
        self.assertEqual(matches[0]["file"], "billing.py")

    def test_08_game_builder(self):
        """Verify Game Factory generates sovereign Godot 4 project structure"""
        gb = GameBuilder(self.mock_brain, self.temp_dir)
        res = gb.build_game("2D Space Invaders Game", game_name="space_invaders")
        self.assertTrue(res["success"])
        app_dir = self.temp_dir / "apps" / "space_invaders"
        self.assertTrue((app_dir / "project.godot").exists())
        self.assertTrue((app_dir / "scripts" / "Player.gd").exists())
        self.assertTrue((app_dir / "scenes" / "Main.tscn").exists())
        self.assertTrue((app_dir / "run_godot.bat").exists())

    def test_09_android_builder(self):
        """Verify Android builder generates project structure and build runner"""
        ab = AndroidAppBuilder(self.mock_brain, self.temp_dir)
        res = ab.build_and_deploy("Bluetooth Scanner Android App", app_name="bt_scanner")
        self.assertTrue(res["success"])
        app_dir = self.temp_dir / "apps" / "bt_scanner"
        self.assertTrue(app_dir.exists())
        self.assertTrue((app_dir / "build_and_install.bat").exists())

    def test_10_document_builder(self):
        """Verify Document Factory generates reports (PDF/HTML, CSV, Markdown)"""
        db = DocumentBuilder(self.mock_brain, self.temp_dir)
        pdf_res = db.generate_report("AI Systems Architecture", doc_type="pdf")
        self.assertTrue(pdf_res["success"])
        self.assertTrue(Path(pdf_res["document_path"]).exists())

        csv_res = db.generate_report("Financial Quarterly Growth", doc_type="csv")
        self.assertTrue(csv_res["success"])
        self.assertTrue(Path(csv_res["document_path"]).exists())

    def test_11_adb_and_git_tools(self):
        """Verify ADB and Git tool interfaces"""
        devices = ADBTool.get_connected_devices()
        self.assertIsInstance(devices, list)

        gt = GitTool(self.temp_dir)
        init_res = gt.init_repo()
        self.assertTrue(init_res["success"])
        status = gt.status()
        self.assertTrue(status["success"])

if __name__ == "__main__":
    unittest.main()
