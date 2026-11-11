from typing import Tuple, Dict, Any
from core.mission import RiskLevel, AutonomyLevel
from config import console

class PermissionManager:
    """
    Manages 4-tier risk assessment and autonomy levels (0 to 4) for OmniDev.
    """
    def __init__(self, default_autonomy: AutonomyLevel = AutonomyLevel.LEVEL_3):
        self.autonomy_level: AutonomyLevel = default_autonomy
        self.audit_log: list = []

    def assess_risk(self, tool_name: str, params: Dict[str, Any]) -> RiskLevel:
        low_tools = ["read_file", "list_directory", "git_status", "run_tests", "search_code"]
        med_tools = ["write_file", "install_dependency", "build_docker", "git_commit", "terminal_exec"]
        high_tools = ["delete_file", "git_push", "adb_install_apk", "db_migration", "drop_table"]
        crit_tools = ["system_config_change", "force_push", "wipe_database", "credential_operation"]

        if tool_name in crit_tools:
            return RiskLevel.CRITICAL
        if tool_name in high_tools:
            return RiskLevel.HIGH
        if tool_name in med_tools:
            return RiskLevel.MEDIUM
        return RiskLevel.LOW

    def can_execute_autonomously(self, tool_name: str, params: Dict[str, Any]) -> Tuple[bool, RiskLevel, str]:
        risk = self.assess_risk(tool_name, params)
        self.audit_log.append({"tool": tool_name, "params": params, "risk": risk.value})

        if self.autonomy_level == AutonomyLevel.LEVEL_0:
            return False, risk, "Manual mode: confirmation required."
        if self.autonomy_level == AutonomyLevel.LEVEL_1:
            return False, risk, "Level 1: Tool execution requires confirmation."
        if self.autonomy_level == AutonomyLevel.LEVEL_2:
            if risk == RiskLevel.LOW:
                return True, risk, "Approved (LOW risk)."
            return False, risk, f"{risk.value} risk requires approval."
        if self.autonomy_level == AutonomyLevel.LEVEL_3:
            if risk in [RiskLevel.LOW, RiskLevel.MEDIUM]:
                return True, risk, "Approved (LOW/MEDIUM risk)."
            return False, risk, f"{risk.value} risk requires approval."
        if self.autonomy_level == AutonomyLevel.LEVEL_4:
            if risk == RiskLevel.CRITICAL:
                return False, risk, "CRITICAL actions always require approval."
            return True, risk, "Approved (Full Autonomy)."

        return False, risk, "Policy denied."
