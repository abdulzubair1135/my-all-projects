# Security and Role-Based Access Control (RBAC)

ProjectFlow Intelligence implements defense-in-depth security with strict tenant isolation, stateless authentication, and cryptographic token verification.

---

## Role Hierarchy and Permissions

| Role | Scope | Key Permissions |
|---|---|---|
| `ADMINISTRATOR` | Global Platform | Global overview, promote/demote user roles, inspect system health, read all audit logs |
| `OWNER` | Organization / Workspace | Manage workspace settings, add/remove workspace members, configure workflows |
| `MANAGER` | Workspace / Project | Create projects, assign tasks, run Risk Radar, create/approve What-If scenarios |
| `MEMBER` | Assigned Projects | View assigned tasks, move task statuses, edit progress percentage |
| `VIEWER` | Workspace | Read-only observation of projects and Kanban boards |

---

## Authentication Mechanism
- **Bearer Token Authorization**: Client requests include `Authorization: Bearer <token>` in the HTTP header.
- **JwtAuthenticationFilter**: Validates cryptographic signature and claims (`sub`, `email`, `role`, `workspaceIds`).
- **Dev Token Fallback**: In local development environments, pre-configured tokens (`dev-admin-token`, `dev-manager-token`, `dev-member-token`) allow friction-free testing of role permissions.
- **Unauthorized Entry Point**: Unauthenticated requests return immediate `401 Unauthorized` responses without exposing server stack traces.

---

## Multi-Tenant Workspace Isolation
- Direct database repository queries always filter by `workspace_id`.
- Attempting to access or mutate an entity belonging to another workspace yields a `403 Forbidden` response and records a security audit violation.
