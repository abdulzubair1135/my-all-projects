import pytest
import os
import tempfile
from pathlib import Path
from agent.security.path_guard import PathGuard, SecurityException
from agent.security.secret_scanner import SecretScanner
from agent.execution.command_policy import CommandPolicyEngine, CommandCategory

def test_path_guard_valid_paths():
    with tempfile.TemporaryDirectory() as tmpdir:
        resolved = PathGuard.validate_and_resolve(tmpdir, "src/components/App.jsx")
        assert str(resolved).startswith(str(Path(tmpdir).resolve()))

def test_path_guard_traversal_rejection():
    with tempfile.TemporaryDirectory() as tmpdir:
        with pytest.raises(SecurityException):
            PathGuard.validate_and_resolve(tmpdir, "../../../etc/passwd")

        with pytest.raises(SecurityException):
            PathGuard.validate_and_resolve(tmpdir, "..\\..\\Windows\\System32")

def test_path_guard_reserved_devices_and_unc():
    with tempfile.TemporaryDirectory() as tmpdir:
        with pytest.raises(SecurityException):
            PathGuard.validate_and_resolve(tmpdir, "CON.txt")

        with pytest.raises(SecurityException):
            PathGuard.validate_and_resolve(tmpdir, "\\\\malicious-server\\share\\hack.exe")

def test_command_policy_categories():
    # Safe commands
    cat, _ = CommandPolicyEngine.evaluate("npm install express")
    assert cat == CommandCategory.SAFE

    cat, _ = CommandPolicyEngine.evaluate("npm test")
    assert cat == CommandCategory.SAFE

    cat, _ = CommandPolicyEngine.evaluate("python -m pytest tests/")
    assert cat == CommandCategory.SAFE

    # Caution commands
    cat, _ = CommandPolicyEngine.evaluate("curl https://example.com/data.json")
    assert cat == CommandCategory.CAUTION

    cat, _ = CommandPolicyEngine.evaluate("git push origin main")
    assert cat == CommandCategory.CAUTION

    # Blocked commands
    cat, _ = CommandPolicyEngine.evaluate("format C: /fs:NTFS")
    assert cat == CommandCategory.BLOCKED

    cat, _ = CommandPolicyEngine.evaluate("rm -rf /")
    assert cat == CommandCategory.BLOCKED

    cat, _ = CommandPolicyEngine.evaluate("powershell -ExecutionPolicy Bypass -Command Get-Process")
    assert cat == CommandCategory.BLOCKED

    cat, _ = CommandPolicyEngine.evaluate("cat ~/.ssh/id_rsa")
    assert cat == CommandCategory.BLOCKED

def test_secret_scanner_redaction():
    text = "Here is my secret sk-abc12345678901234567890 and AWS key AKIAIOSFODNN7EXAMPLE"
    redacted, count = SecretScanner.scan_and_redact(text)
    assert count >= 2
    assert "sk-abc" not in redacted
    assert "AKIAIOSF" not in redacted
    assert "[REDACTED_API_KEY]" in redacted
    assert "[REDACTED_AWS_KEY]" in redacted

def test_secret_scanner_forbidden_files():
    assert SecretScanner.is_forbidden_file(".env") is True
    assert SecretScanner.is_forbidden_file("id_rsa") is True
    assert SecretScanner.is_forbidden_file("server/cert.pem") is True
    assert SecretScanner.is_forbidden_file("src/App.jsx") is False
