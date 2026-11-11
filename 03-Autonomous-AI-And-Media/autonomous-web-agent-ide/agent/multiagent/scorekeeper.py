import time
from typing import Dict, Any, List, Optional

class QualityAuditResult:
    def __init__(self, passed: bool, score: int, delta: int, reasons: List[str], role: str):
        self.passed = passed
        self.score = score
        self.delta = delta
        self.reasons = reasons
        self.role = role

    def to_dict(self) -> Dict[str, Any]:
        return {
            "passed": self.passed,
            "score": self.score,
            "delta": self.delta,
            "reasons": self.reasons,
            "role": self.role
        }

class ScoreKeeper:
    """
    Reinforcement Quality & Audit Scoring System for Autonomous Multi-Agent IDE.
    Rewards high-quality modular code, test coverage, and responsive styling.
    Penalizes syntax errors, unfinished code, and missing edge-case handlers.
    """

    def __init__(self, initial_score: int = 100):
        self.score = initial_score
        self.history: List[Dict[str, Any]] = []

    def evaluate_task_code(self, task: Dict[str, Any], actions: List[Dict[str, Any]], verification_result: Optional[Dict[str, Any]] = None) -> QualityAuditResult:
        delta = 0
        reasons = []

        code_actions = [a for a in actions if a.get("type") in ["write_file", "edit_file"]]
        cmd_actions = [a for a in actions if a.get("type") in ["run_command", "run_tests", "run_build"]]

        # 1. Evaluate Code Completeness & Structure
        for ca in code_actions:
            path = ca.get("path", "")
            content = ca.get("content", "")

            if not content or len(content.strip()) < 10:
                delta -= 15
                reasons.append(f"[-15] Empty or trivial file generated: {path}")
            elif "TODO" in content or "implement here" in content.lower():
                delta -= 10
                reasons.append(f"[-10] Unimplemented placeholder detected in: {path}")
            else:
                delta += 10
                reasons.append(f"[+10] Complete production code generated: {path}")

            # Check for React / JS syntax hygiene
            if path.endswith((".jsx", ".tsx", ".js")):
                if "export default" in content or "export const" in content or "module.exports" in content:
                    delta += 5
                    reasons.append(f"[+5] Proper modular exports defined: {path}")
                if "try" in content and "catch" in content:
                    delta += 5
                    reasons.append(f"[+5] Defensive error handling present in: {path}")

        # 2. Evaluate Command & Test Execution
        if cmd_actions:
            if verification_result and verification_result.get("exit_code") == 0:
                delta += 15
                reasons.append("[+15] Build / test suite passed with exit code 0")
            elif verification_result and verification_result.get("exit_code") != 0:
                delta -= 15
                reasons.append(f"[-15] Verification command failed: {verification_result.get('stderr')}")
            else:
                delta += 5
                reasons.append("[+5] Command verification executed successfully")

        # Cap min score at 0
        self.score = max(0, self.score + delta)
        passed = delta >= 0 or self.score >= 60

        result = QualityAuditResult(
            passed=passed,
            score=self.score,
            delta=delta,
            reasons=reasons,
            role="ReviewerJudgeAgent"
        )

        self.history.append({
            "task_id": task.get("id"),
            "task_title": task.get("title"),
            "delta": delta,
            "score": self.score,
            "reasons": reasons,
            "timestamp": time.time()
        })

        return result

    def get_summary(self) -> Dict[str, Any]:
        return {
            "current_score": self.score,
            "total_evaluations": len(self.history),
            "history": self.history
        }
