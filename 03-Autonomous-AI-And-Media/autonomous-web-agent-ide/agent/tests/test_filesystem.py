import pytest
import tempfile
from pathlib import Path
from agent.execution.filesystem import FileSystem

def test_filesystem_write_and_read():
    with tempfile.TemporaryDirectory() as tmpdir:
        hash_val = FileSystem.write_file(tmpdir, "src/test.txt", "Hello Sandbox")
        assert hash_val is not None

        content, read_hash = FileSystem.read_file(tmpdir, "src/test.txt")
        assert content == "Hello Sandbox"
        assert read_hash == hash_val

def test_filesystem_conflict_detection():
    with tempfile.TemporaryDirectory() as tmpdir:
        FileSystem.write_file(tmpdir, "config.json", '{"port": 3000}')

        # Try editing with wrong expected hash
        with pytest.raises(ValueError, match="Conflict detected"):
            FileSystem.edit_file(tmpdir, "config.json", content='{"port": 4000}', expected_hash="wrong_hash_val")

def test_filesystem_list_and_search():
    with tempfile.TemporaryDirectory() as tmpdir:
        FileSystem.write_file(tmpdir, "server.js", "const express = require('express');")
        FileSystem.write_file(tmpdir, "client/App.jsx", "export default function App() {}")

        files = FileSystem.list_files(tmpdir)
        paths = [f["path"] for f in files]
        assert "server.js" in paths
        assert "client/App.jsx" in paths

        search_res = FileSystem.search_files(tmpdir, "express")
        assert "server.js" in search_res
