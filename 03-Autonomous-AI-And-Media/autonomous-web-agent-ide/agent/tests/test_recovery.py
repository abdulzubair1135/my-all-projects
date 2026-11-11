import pytest
from agent.recovery.error_analyzer import ErrorAnalyzer
from agent.recovery.loop_detector import LoopDetector
from agent.recovery.retry_manager import RetryManager

def test_error_analyzer_categorization():
    err = ErrorAnalyzer.analyze_command_failure("node index.js", 1, "", "Error: Cannot find module 'express'")
    assert err["category"] == "missing_dependency"
    assert "Cannot find module" in err["error_snippet"]

    err2 = ErrorAnalyzer.analyze_command_failure("node index.js", 1, "", "Error: listen EADDRINUSE: address already in use :::3000")
    assert err2["category"] == "port_conflict"

def test_loop_detector_fingerprinting():
    detector = LoopDetector(max_same_error=3, max_total_iterations=10)

    # First occurrence -> OK
    assert detector.record_error("npm run build", 1, "SyntaxError: Unexpected token") is True
    # Second occurrence -> OK
    assert detector.record_error("npm run build", 1, "SyntaxError: Unexpected token") is True
    # Third occurrence -> Exceeds max_same_error (3) -> Halts (Returns False)
    assert detector.record_error("npm run build", 1, "SyntaxError: Unexpected token") is False

def test_retry_manager_strategies():
    mgr = RetryManager(max_retries_per_task=3)
    assert mgr.should_retry(0) is True
    assert mgr.should_retry(2) is True
    assert mgr.should_retry(3) is False
    assert mgr.get_strategy_for_attempt(1) == "direct_fix"
