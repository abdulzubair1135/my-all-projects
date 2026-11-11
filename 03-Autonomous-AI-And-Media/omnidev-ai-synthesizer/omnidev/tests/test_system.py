import unittest
import os
import shutil
from pathlib import Path

# Add omnidev root to sys.path
import sys
OMNIDEV_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(OMNIDEV_DIR))

from tools.terminal import run_terminal_command_sync
from tools.file_manager import FileManager
from tools.codebase_inspector import CodebaseInspector
from tools.process_manager import ProcessManager
from tools.e2e_tester import E2ETester
from core.safety import SafetyGuard

class TestOmniDevCore(unittest.TestCase):
    def setUp(self):
        self.test_dir = OMNIDEV_DIR / "tests" / "scratch_test"
        self.test_dir.mkdir(parents=True, exist_ok=True)
        self.file_mgr = FileManager(self.test_dir)

    def tearDown(self):
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_terminal_and_safety(self):
        # Test safe command
        res = run_terminal_command_sync("python --version")
        self.assertEqual(res.exit_code, 0)
        self.assertIn("Python", res.stdout)

        # Test dangerous command blocked by safety guard
        is_safe, reason = SafetyGuard.check_command("format C:")
        self.assertFalse(is_safe)

    def test_file_manager_and_backups(self):
        test_file = self.test_dir / "sample.py"
        self.file_mgr.write_file(test_file, "def greet():\n    return 'hello'\n")
        self.assertTrue(test_file.exists())

        # Test patch
        patched = self.file_mgr.patch_file(test_file, "'hello'", "'world'")
        self.assertTrue(patched)
        content = self.file_mgr.read_file(test_file)
        self.assertIn("'world'", content)

        # Verify backup exists
        backups = list((self.test_dir / ".omnidev_backups").glob("*.bak"))
        self.assertGreaterEqual(len(backups), 1)

    def test_codebase_inspector(self):
        inspector = CodebaseInspector(OMNIDEV_DIR)
        proj_type = inspector.detect_project_type()
        self.assertEqual(proj_type["type"], "python")
        summary = inspector.generate_context_summary()
        self.assertIn("Existing Project Context", summary)
        self.assertIn("Python Symbols", summary)

    def test_process_and_port_discovery(self):
        free_port = ProcessManager.find_free_port(9000, 9100)
        self.assertGreaterEqual(free_port, 9000)
        proc_mgr = ProcessManager()
        self.assertFalse(proc_mgr.is_port_open(free_port))

if __name__ == "__main__":
    unittest.main()
