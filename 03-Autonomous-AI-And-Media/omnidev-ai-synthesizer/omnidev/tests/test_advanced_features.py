import sys
import unittest
import tempfile
import shutil
import sqlite3
from pathlib import Path

OMNIDEV_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(OMNIDEV_DIR))

from tools.env_doctor import EnvironmentDoctor
from tools.db_tool import DatabaseTool
from tools.dep_intelligence import DependencyIntelligence
from tools.security_scanner import SecurityScanner
from core.project_graph import ProjectKnowledgeGraph
from core.memory_vault import MemoryVault
from core.error_memory import ErrorMemory

class TestOmniDevAdvancedFeatures(unittest.TestCase):
    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_environment_doctor(self):
        diag = EnvironmentDoctor.diagnose()
        self.assertTrue(diag["success"])
        self.assertIn("python", diag["tools"])
        self.assertTrue(diag["tools"]["python"]["installed"])

    def test_database_tool_inspect_and_query(self):
        db_file = self.temp_dir / "test.db"
        conn = sqlite3.connect(str(db_file))
        conn.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT)")
        conn.execute("INSERT INTO users (name) VALUES ('Alice')")
        conn.commit()
        conn.close()

        schema = DatabaseTool.inspect_sqlite_schema(db_file)
        self.assertTrue(schema["success"])
        self.assertIn("users", schema["tables"])

        query_res = DatabaseTool.run_safe_query(db_file, "SELECT * FROM users")
        self.assertTrue(query_res["success"])
        self.assertEqual(len(query_res["rows"]), 1)
        self.assertEqual(query_res["rows"][0]["name"], "Alice")

    def test_security_scanner_secret_detection(self):
        # Create a file with a simulated leak
        leak_file = self.temp_dir / "config_sample.py"
        leak_file.write_text("API_KEY = 'sk-1234567890abcdef1234567890abcdef'", encoding="utf-8")
        
        scanner = SecurityScanner(self.temp_dir)
        audit = scanner.full_audit()
        self.assertFalse(audit["clean"])
        self.assertIn("config_sample.py", audit["secret_leaks"])

    def test_project_knowledge_graph_ast(self):
        py_file = self.temp_dir / "auth_service.py"
        py_file.write_text("""
class AuthService:
    def login_user(self, username, password):
        return True
""", encoding="utf-8")

        graph = ProjectKnowledgeGraph(self.temp_dir)
        matches = graph.search_code_nl("Login user authentication")
        self.assertTrue(len(matches) > 0)
        self.assertIn("auth_service.py", matches[0]["file"])

    def test_dependency_intelligence(self):
        pkg_file = self.temp_dir / "package.json"
        pkg_file.write_text('{"dependencies": {"express": "4.18.2"}}', encoding="utf-8")
        
        di = DependencyIntelligence(self.temp_dir)
        info = di.scan_dependencies()
        self.assertEqual(info["package_manager"], "npm")
        self.assertIn("express", info["dependencies"])

if __name__ == "__main__":
    unittest.main()
