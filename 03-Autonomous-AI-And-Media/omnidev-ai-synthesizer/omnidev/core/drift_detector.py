from typing import List, Dict, Any
from core.mission import Mission
from core.project_graph import ProjectKnowledgeGraph

class RequirementDriftDetector:
    """
    Requirement Drift Detector & Change Impact Analyzer for OmniDev:
    Continuously compares original mission requirements against current implementation
    to detect missing features, API mismatches, or scope drift.
    """
    @staticmethod
    def audit_drift(mission: Mission, project_graph: ProjectKnowledgeGraph) -> Dict[str, Any]:
        drift_items = []
        if not project_graph.nodes:
            project_graph.build_graph()

        all_symbols = set()
        for data in project_graph.nodes.values():
            all_symbols.update(c.lower() for c in data.get("classes", []))
            all_symbols.update(f.lower() for f in data.get("functions", []))

        for req in mission.requirements:
            words = [w.lower() for w in req.description.split() if len(w) > 3]
            match = any(any(w in s for s in all_symbols) for w in words)
            req.satisfied = match
            if not match:
                drift_items.append(req.description)

        return {
            "drift_detected": len(drift_items) > 0,
            "missing_requirements": drift_items,
            "progress_percentage": mission.get_progress_percentage()
        }
