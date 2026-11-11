import pytest
import asyncio
from pathlib import Path
import sys

AGENT_ROOT = Path(__file__).resolve().parent.parent
if str(AGENT_ROOT) not in sys.path:
    sys.path.insert(0, str(AGENT_ROOT))

from run_20_benchmark import BENCHMARK_SCENARIOS, run_single_test

@pytest.mark.asyncio
@pytest.mark.parametrize("scenario", BENCHMARK_SCENARIOS, ids=[s["name"] for s in BENCHMARK_SCENARIOS])
async def test_agent_benchmark_scenario(scenario):
    """Evaluates each of the 20 benchmark applications against the autonomous agent pipeline."""
    result = await run_single_test(scenario)
    assert result["passed"] is True, f"Benchmark test '{scenario['name']}' failed: {result.get('error')}"
    assert result["files"] >= 3, f"Expected >= 3 files generated, got {result['files']}"
    assert result["score"] >= 80, f"Expected score >= 80, got {result['score']}"
