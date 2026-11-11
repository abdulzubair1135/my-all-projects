# -*- coding: utf-8 -*-
"""
project_memory.py
Persistent Long-Term Memory Ledger for Autonomous Web-Agent IDE.

Stores project identity, architectural decisions, user preferences,
and milestone history so AI providers (DeepSeek, Gemini, etc.) never lose context.
"""

import os
import sqlite3
import json
import time
from pathlib import Path
from typing import Dict, Any, List, Optional


class ProjectMemoryManager:
    """
    Persistent SQLite Memory Ledger.
    Ensures DeepSeek and other AI providers retain full context across turns.
    """

    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            data_dir = Path(__file__).resolve().parent.parent.parent / 'data'
            data_dir.mkdir(parents=True, exist_ok=True)
            self.db_path = str(data_dir / 'project_memory.sqlite')
        else:
            self.db_path = db_path
        self._ensure_tables()

    def _conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, timeout=10)
        conn.row_factory = sqlite3.Row
        return conn

    def _ensure_tables(self):
        with self._conn() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS project_profiles (
                    workspace TEXT PRIMARY KEY,
                    project_name TEXT NOT NULL,
                    project_type TEXT,
                    ui_style TEXT,
                    game_engine TEXT,
                    asset_strategy TEXT,
                    quality_tier TEXT DEFAULT 'AAA_PRODUCTION',
                    notes TEXT,
                    created_at REAL,
                    updated_at REAL
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS project_decisions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    workspace TEXT NOT NULL,
                    topic TEXT NOT NULL,
                    decision TEXT NOT NULL,
                    rationale TEXT,
                    timestamp REAL
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS project_milestones (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    workspace TEXT NOT NULL,
                    title TEXT NOT NULL,
                    details TEXT,
                    timestamp REAL
                )
            """)
            conn.commit()

    def save_profile(
        self,
        workspace: str,
        project_name: str,
        project_type: str = 'General',
        ui_style: str = 'Modern',
        game_engine: str = 'None',
        asset_strategy: str = 'Autonomous Procedural Generation',
        quality_tier: str = 'AAA_PRODUCTION',
        notes: str = ''
    ):
        now = time.time()
        norm_ws = str(Path(workspace).resolve()).lower()
        with self._conn() as conn:
            conn.execute("""
                INSERT INTO project_profiles (workspace, project_name, project_type, ui_style, game_engine, asset_strategy, quality_tier, notes, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(workspace) DO UPDATE SET
                    project_name=excluded.project_name,
                    project_type=excluded.project_type,
                    ui_style=excluded.ui_style,
                    game_engine=excluded.game_engine,
                    asset_strategy=excluded.asset_strategy,
                    quality_tier=excluded.quality_tier,
                    notes=excluded.notes,
                    updated_at=excluded.updated_at
            """, (norm_ws, project_name, project_type, ui_style, game_engine, asset_strategy, quality_tier, notes, now, now))
            conn.commit()

    def add_decision(self, workspace: str, topic: str, decision: str, rationale: str = ''):
        norm_ws = str(Path(workspace).resolve()).lower()
        with self._conn() as conn:
            conn.execute("""
                INSERT INTO project_decisions (workspace, topic, decision, rationale, timestamp)
                VALUES (?, ?, ?, ?, ?)
            """, (norm_ws, topic, decision, rationale, time.time()))
            conn.commit()

    def add_milestone(self, workspace: str, title: str, details: str = ''):
        norm_ws = str(Path(workspace).resolve()).lower()
        with self._conn() as conn:
            conn.execute("""
                INSERT INTO project_milestones (workspace, title, details, timestamp)
                VALUES (?, ?, ?, ?)
            """, (norm_ws, title, details, time.time()))
            conn.commit()

    def get_profile(self, workspace: str) -> Optional[Dict[str, Any]]:
        norm_ws = str(Path(workspace).resolve()).lower()
        with self._conn() as conn:
            row = conn.execute("SELECT * FROM project_profiles WHERE workspace = ?", (norm_ws,)).fetchone()
            return dict(row) if row else None

    def get_decisions(self, workspace: str) -> List[Dict[str, Any]]:
        norm_ws = str(Path(workspace).resolve()).lower()
        with self._conn() as conn:
            rows = conn.execute("SELECT * FROM project_decisions WHERE workspace = ? ORDER BY timestamp ASC", (norm_ws,)).fetchall()
            return [dict(r) for r in rows]

    def get_milestones(self, workspace: str) -> List[Dict[str, Any]]:
        norm_ws = str(Path(workspace).resolve()).lower()
        with self._conn() as conn:
            rows = conn.execute("SELECT * FROM project_milestones WHERE workspace = ? ORDER BY timestamp DESC LIMIT 5", (norm_ws,)).fetchall()
            return [dict(r) for r in rows]

    def get_project_memory_prompt(self, workspace: str) -> str:
        """
        Generate a high-density, authoritative memory chronicle block
        for prepending to AI provider prompts.
        """
        profile = self.get_profile(workspace)
        if not profile:
            return ""

        decisions = self.get_decisions(workspace)
        milestones = self.get_milestones(workspace)

        lines = [
            "==================================================================",
            "[PROJECT CHRONICLE & PERSISTENT MEMORY LEDGER]",
            f"• Target Project: {profile.get('project_name')} ({profile.get('project_type')})",
            f"• UI / Design System: {profile.get('ui_style')}",
            f"• Engine / Technology Stack: {profile.get('game_engine')}",
            f"• Asset Generation Strategy: {profile.get('asset_strategy')}",
            f"• Quality Tier: {profile.get('quality_tier')}",
        ]

        if profile.get('notes'):
            lines.append(f"• Core Specifications: {profile.get('notes')}")

        if decisions:
            lines.append("• Key Architectural Decisions:")
            for d in decisions[-6:]:
                lines.append(f"  - [{d['topic']}]: {d['decision']} (Rationale: {d.get('rationale', 'N/A')})")

        if milestones:
            lines.append("• Verified Project Milestones:")
            for m in milestones:
                lines.append(f"  - [PASS] {m['title']}: {m.get('details', '')}")

        lines.append("[CRITICAL INSTRUCTION: Maintain 100% strict continuity with these specifications. Never discard or reset established project architecture.]")
        lines.append("==================================================================\n")
        return "\n".join(lines)
