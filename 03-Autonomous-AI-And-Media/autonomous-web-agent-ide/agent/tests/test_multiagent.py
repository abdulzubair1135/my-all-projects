import pytest
import asyncio
import tempfile
import os
from pathlib import Path

from agent.multiagent.scorekeeper import ScoreKeeper
from agent.multiagent.roles import ArchitectAgent, EngineerAgent, ReviewerJudgeAgent, RefinerAgent
from agent.multiagent.team_orchestrator import MultiAgentTeamOrchestrator
from agent.browser.providers.mock_provider import MockLocalProvider

@pytest.mark.asyncio
async def test_scorekeeper_rewards_and_penalties():
    sk = ScoreKeeper(initial_score=100)
    task = {"id": "task-1", "title": "Implement Calculator"}

    # Test clean code reward (+10 for complete, +5 for export, +5 for try/catch)
    good_actions = [{
        "type": "write_file",
        "path": "src/App.jsx",
        "content": "import React from 'react';\nexport default function App() { try { return <div>Ok</div>; } catch(e) { return null; } }"
    }]
    audit = sk.evaluate_task_code(task, good_actions)
    assert audit.passed is True
    assert audit.delta > 0
    assert audit.score > 100

    # Test penalty for placeholder code
    bad_actions = [{
        "type": "write_file",
        "path": "src/dummy.js",
        "content": "// TODO: implement here"
    }]
    bad_audit = sk.evaluate_task_code(task, bad_actions)
    assert bad_audit.delta < 0

@pytest.mark.asyncio
async def test_multiagent_roles_collaboration():
    provider = MockLocalProvider()
    architect = ArchitectAgent(provider)
    engineer = EngineerAgent(provider)
    reviewer = ReviewerJudgeAgent(provider)
    refiner = RefinerAgent(provider)

    # 1. Architect Plans
    plan = await architect.plan("Build a modern scientific calculator")
    assert len(plan.tasks) >= 2

    # 2. Engineer Implements
    task_1 = {"id": "task-1", "title": "Initialize React Vite project", "description": "Setup files"}
    resp = await engineer.implement_task(task_1, "Workspace is clean")
    assert len(resp.actions) >= 1

    # 3. Reviewer Judges
    review = await reviewer.review_code(task_1, [a.model_dump() for a in resp.actions])
    assert "score" in review

    # 4. Refiner Refines
    refined = await refiner.refine(task_1, [a.model_dump() for a in resp.actions], "Add comments", ["Add export"])
    assert len(refined.actions) >= 1

@pytest.mark.asyncio
async def test_multiagent_full_autonomous_loop():
    tmp_dir = tempfile.mkdtemp()
    provider = MockLocalProvider()
    orchestrator = MultiAgentTeamOrchestrator(
        project_id="multiagent_calc_test",
        run_id="run_1",
        workspace_root=tmp_dir,
        provider=provider,
        db_path=os.path.join(tmp_dir, ".agent_state.sqlite"),
        approval_mode="AUTO"
    )

    success = await orchestrator.run("Make a modern calculator web app with React")
    assert success is True
    assert (Path(tmp_dir) / "package.json").exists()
    assert (Path(tmp_dir) / "src" / "App.jsx").exists()
    assert orchestrator.scorekeeper.score >= 100
