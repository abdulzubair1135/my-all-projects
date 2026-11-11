from typing import List, Dict, Any, Optional

try:
    from protocol.schemas import ProjectPlan, TaskNode
except ImportError:
    from ..protocol.schemas import ProjectPlan, TaskNode

class TaskManager:
    def __init__(self, plan: Optional[ProjectPlan] = None):
        self.tasks: Dict[str, Dict[str, Any]] = {}
        self.dependencies: Dict[str, List[str]] = {}
        if plan:
            self.load_plan(plan)

    def load_plan(self, plan: ProjectPlan):
        self.tasks.clear()
        self.dependencies.clear()

        for idx, t in enumerate(plan.tasks):
            self.tasks[t.id] = {
                "id": t.id,
                "title": t.title,
                "description": t.description,
                "status": "PENDING",  # PENDING, RUNNING, COMPLETED, FAILED, BLOCKED
                "order_index": idx,
                "retry_count": 0,
                "error_message": None
            }
            self.dependencies[t.id] = list(t.depends_on)

    def get_next_available_task(self) -> Optional[Dict[str, Any]]:
        """
        Finds the next PENDING task whose dependencies are all COMPLETED with resilient ID matching.
        """
        for task_id, task in self.tasks.items():
            if task["status"] == "PENDING":
                deps = self.dependencies.get(task_id, [])
                if not deps:
                    return task

                deps_satisfied = True
                for dep_id in deps:
                    # Check exact match or normalized match (task-1 vs task_1)
                    norm_dep = dep_id.replace("_", "-")
                    matched_status = None
                    for t_id, t_data in self.tasks.items():
                        if t_id == dep_id or t_id.replace("_", "-") == norm_dep:
                            matched_status = t_data.get("status")
                            break
                    if matched_status != "COMPLETED":
                        deps_satisfied = False
                        break

                if deps_satisfied:
                    return task
        return None

    def update_task_status(self, task_id: str, status: str, error_message: Optional[str] = None):
        if task_id in self.tasks:
            self.tasks[task_id]["status"] = status
            if error_message is not None:
                self.tasks[task_id]["error_message"] = error_message
            if status == "FAILED":
                self.tasks[task_id]["retry_count"] += 1

    def are_all_tasks_completed(self) -> bool:
        if not self.tasks:
            return False
        return all(t["status"] == "COMPLETED" for t in self.tasks.values())

    def get_all_tasks(self) -> List[Dict[str, Any]]:
        return list(self.tasks.values())
