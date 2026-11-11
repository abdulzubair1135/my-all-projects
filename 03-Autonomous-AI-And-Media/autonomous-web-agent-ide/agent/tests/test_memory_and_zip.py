# -*- coding: utf-8 -*-
"""
test_memory_and_zip.py
Automated tests for ProjectMemoryManager and Multi-Part ZipChunker.
"""

import os
import shutil
import tempfile
import pytest
from pathlib import Path
from core.project_memory import ProjectMemoryManager
from core.zip_chunker import create_chunked_zip, generate_workspace_topology


def test_project_memory_lifecycle():
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "test_mem.sqlite")
        mgr = ProjectMemoryManager(db_path=db_path)

        ws = os.path.join(tmpdir, "workspace_alpha")
        os.makedirs(ws, exist_ok=True)

        mgr.save_profile(
            workspace=ws,
            project_name="Retro Arcade",
            project_type="Godot C# 2D Game",
            ui_style="Retro 8-Bit CRT",
            game_engine="Godot 4.3",
            asset_strategy="Procedural Pixel Art",
            quality_tier="AAA_PRODUCTION",
            notes="Full game project test"
        )

        profile = mgr.get_profile(ws)
        assert profile is not None
        assert profile["project_name"] == "Retro Arcade"
        assert profile["game_engine"] == "Godot 4.3"

        mgr.add_decision(ws, "Architecture", "Component-Entity", "Modular game loop")
        decisions = mgr.get_decisions(ws)
        assert len(decisions) == 1
        assert decisions[0]["topic"] == "Architecture"

        mgr.add_milestone(ws, "Initial Commit", "Created project structure")
        milestones = mgr.get_milestones(ws)
        assert len(milestones) == 1

        prompt = mgr.get_project_memory_prompt(ws)
        assert "[PROJECT CHRONICLE & PERSISTENT MEMORY LEDGER]" in prompt
        assert "Retro Arcade" in prompt
        assert "Godot 4.3" in prompt


def test_zip_chunker_single():
    with tempfile.TemporaryDirectory() as tmpdir:
        ws = os.path.join(tmpdir, "test_project")
        os.makedirs(os.path.join(ws, "src"), exist_ok=True)
        with open(os.path.join(ws, "src", "main.py"), "w") as f:
            f.write("print('hello world')\n")

        res = create_chunked_zip(ws, max_chunk_mb=38.0)
        assert res["is_chunked"] is False
        assert len(res["archive_paths"]) == 1
        assert os.path.exists(res["archive_paths"][0])
        assert res["parts_count"] == 1


def test_zip_chunker_multi_part():
    with tempfile.TemporaryDirectory() as tmpdir:
        ws = os.path.join(tmpdir, "test_project_large")
        os.makedirs(ws, exist_ok=True)

        # Write dummy file with 50KB random data (incompressible)
        dummy_data = os.urandom(50000)
        with open(os.path.join(ws, "data.bin"), "wb") as f:
            f.write(dummy_data)

        # Chunk with tiny threshold (0.01 MB = ~10KB)
        res = create_chunked_zip(ws, max_chunk_mb=0.01, prefix_name="split_archive")
        assert res["is_chunked"] is True
        assert res["parts_count"] >= 2
        assert res["manifest_path"] is not None
        assert os.path.exists(res["manifest_path"])

        for part in res["archive_paths"]:
            assert os.path.exists(part)


def test_workspace_topology_generation():
    with tempfile.TemporaryDirectory() as tmpdir:
        ws = os.path.join(tmpdir, "my_app")
        os.makedirs(os.path.join(ws, "frontend"), exist_ok=True)
        with open(os.path.join(ws, "frontend", "index.html"), "w") as f:
            f.write("<h1>Test</h1>")

        topo = generate_workspace_topology(ws)
        assert "my_app/" in topo
        assert "frontend/" in topo
        assert "index.html" in topo
