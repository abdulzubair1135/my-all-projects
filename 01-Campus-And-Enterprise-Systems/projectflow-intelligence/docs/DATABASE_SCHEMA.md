# Database Schema Specification

The database uses Flyway migrations (`V1__init_schema.sql`) to initialize 19 normalized tables supporting enterprise multi-tenancy, project planning, risk tracking, and compliance auditing.

---

## Normalized Tables

| Table Name | Description | Key Indexes / Constraints |
|---|---|---|
| `organizations` | Root enterprise tenant entity | `PRIMARY KEY (id)` |
| `profiles` | User identity & authentication details | `UNIQUE (email)` |
| `workspaces` | Isolated tenant collaborative boundary | `UNIQUE (organization_id, slug)` |
| `workspace_members` | Role bindings per workspace | `PRIMARY KEY (workspace_id, profile_id)` |
| `workflows` | Workflow configuration containers | `idx_workflows_workspace` |
| `workflow_statuses` | Discrete statuses (TODO, IN_PROGRESS, etc.) | `FOREIGN KEY (workflow_id)` |
| `workflow_transitions` | Permitted state transitions between statuses | `idx_wf_trans_from_to` |
| `projects` | Project initiatives with baseline dates | `idx_projects_workspace_status` |
| `tasks` | Discrete work units with estimated effort | `idx_tasks_project_status`, `idx_tasks_assignee` |
| `task_dependencies` | Predecessor-successor DAG edges | `idx_deps_task_pred` |
| `risk_events` | Historical risk occurrences & active flags | `idx_risks_project_status` |
| `schedule_scenarios` | Alternative What-If schedule models | `idx_scenarios_project` |
| `scenario_changes` | Discrete proposed task date/hour adjustments | `idx_scen_changes_scenario` |
| `sync_operations` | Offline synchronization idempotency queue | `idx_sync_client_seq`, `idx_sync_status` |
| `audit_logs` | Immutable security audit trail | `idx_audit_workspace_timestamp` |

---

## Integrity & Safety Constraints

1. **Foreign Keys**: Cascade delete configured for child entities (e.g. project tasks, scenario changes) while preserving audit logs.
2. **Multi-Column Indices**: High-performance composite indices on `(workspace_id, ...)` prevent sequential scans on large tenant partitions.
3. **Check Constraints**: Enforces positive values for `estimated_hours >= 0` and valid enum strings for roles and priorities.
