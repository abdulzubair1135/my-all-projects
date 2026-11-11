# REST API Specification

All REST API endpoints are served under `/api/v1` and require `Authorization: Bearer <token>` unless otherwise specified.

---

## 1. Authentication Endpoints

### `POST /api/v1/auth/dev-login`
Authenticates or provisions a local test account.
- **Request Body**: `{"email": "admin@projectflow.io"}`
- **Response `200 OK`**:
  ```json
  {
    "token": "dev-admin-token",
    "user": {
      "id": "11111111-1111-1111-1111-111111111111",
      "email": "admin@projectflow.io",
      "fullName": "System Administrator",
      "role": "ADMINISTRATOR",
      "active": true
    }
  }
  ```

### `GET /api/v1/me`
Retrieves currently authenticated user profile.
- **Response `200 OK`**: `UserProfileDto`

---

## 2. Admin Endpoints (`hasAnyRole('ADMINISTRATOR', 'OWNER')`)

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/v1/admin/overview` | Returns aggregate counts for users, workspaces, projects, tasks, risks |
| `GET` | `/api/v1/admin/users?query=&page=0&size=20` | Paginated user accounts list |
| `PATCH` | `/api/v1/admin/users/{id}/role` | Updates global role (`{"role": "MANAGER"}`) |
| `GET` | `/api/v1/admin/workspaces` | Lists all tenant workspaces across the platform |
| `GET` | `/api/v1/admin/projects` | Lists all projects across the platform |
| `GET` | `/api/v1/admin/system/health` | Telemetry: JVM heap, database latency, active threads, schema version |
| `GET` | `/api/v1/admin/audit-events` | Paginated security audit trail entries |

---

## 3. Project Management Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/v1/workspaces` | Lists workspaces accessible to authenticated user |
| `POST` | `/api/v1/workspaces` | Creates a new tenant workspace |
| `GET` | `/api/v1/workspaces/{id}/projects` | Lists all projects in specified workspace |
| `POST` | `/api/v1/workspaces/{id}/projects` | Creates a new project initiative |
| `GET` | `/api/v1/projects/{id}/tasks` | Lists all tasks for a project |
| `POST` | `/api/v1/projects/{id}/tasks` | Creates a work item within a project |
| `POST` | `/api/v1/projects/{id}/risks/evaluate` | Triggers deterministic Risk Radar execution |
| `POST` | `/api/v1/projects/{id}/scenarios/evaluate` | Evaluates What-If schedule scenario against baseline |
| `POST` | `/api/v1/sync/push` | Batch pushes offline client mutations |
| `GET` | `/api/v1/sync/pull` | Fetches incremental changes since last sync timestamp |
