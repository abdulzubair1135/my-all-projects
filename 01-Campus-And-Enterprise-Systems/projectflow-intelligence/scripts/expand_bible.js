// scripts/expand_bible.js
const fs = require('fs');
const path = require('path');

const filePath = path.join(__dirname, '..', 'PROJECTFLOW_MASTER_ARCHITECTURE_AND_CODE_BIBLE.md');
let content = fs.readFileSync(filePath, 'utf8');

const additionalScreenDetails = `
---

# 4.8 DETAILED MOBILE SCREEN-BY-SCREEN INVENTORY & COMPONENT SPECIFICATION

This section details the precise technical anatomy, layout bindings, UI controls, and lifecycle logic for each of the 16 native Android screens.

### Screen 1: Authentication & Tenant Login (\`LoginActivity.java\`)
- **Layout File**: \`activity_login.xml\`
- **Core View Elements**:
  - \`etLoginEmail\` (\`TextInputEditText\`): Captures corporate email address.
  - \`etLoginPassword\` (\`TextInputEditText\`): Captures user password with toggleable mask.
  - \`btnLoginSubmit\` (\`MaterialButton\`): Initiates network authentication.
  - \`pbLoginProgress\` (\`ProgressBar\`): Visual indicator during network round-trip.
- **Controller Logic**:
  1. Validates non-empty credentials and email format.
  2. Executes \`apiService.login(credentials)\` via Retrofit.
  3. On HTTP 200, extracts JWT Bearer token and \`UserProfile\` JSON.
  4. Persists token in \`projectflow_prefs\` via \`SharedPreferences.Editor.putString("auth_token", token)\`.
  5. Navigates to \`MainActivity\` using \`Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_CLEAR_TASK\`.

### Screen 2: Executive Dashboard (\`DashboardFragment.java\`)
- **Layout File**: \`fragment_dashboard.xml\`
- **Core View Elements**:
  - \`tvWelcomeUser\` (\`TextView\`): Greets authenticated user with dynamic time of day.
  - \`tvUserRoleBadge\` (\`TextView\`): Displays uppercase privilege role (ADMINISTRATOR / MANAGER / MEMBER).
  - \`badgeOnlineStatus\` (\`View\`): Live green indicator for active session connectivity.
  - \`radarProjectStatus\` (\`ProjectStatusRadarView\`): Custom 3D canvas ring displaying completion velocity.
  - \`cardCompletedTasks\`, \`cardPendingTasks\`: High-contrast summary cards showing live milestone metrics.
- **Controller Logic**:
  1. \`onViewCreated\` invokes \`viewModel.loadOverviewMetrics()\`.
  2. Queries local Room \`AppDao.getCompletedTaskCount()\` and \`getPendingTaskCount()\`.
  3. Renders the interactive 3D circular progress chart with natural terracotta and sage green sectors.

### Screen 3: Workspaces & Portfolio Explorer (\`ProjectsFragment.java\`)
- **Layout File**: \`fragment_projects.xml\`
- **Core View Elements**:
  - \`rvProjectsList\` (\`RecyclerView\`): Vertical feed of active workspace projects.
  - \`srlProjectsRefresh\` (\`SwipeRefreshLayout\`): Pull-to-refresh container.
  - \`fabNewProject\` (\`FloatingActionButton\`): Spawns project creation dialog for Managers.
- **Controller Logic**:
  - Implements \`ProjectsAdapter\` bound to \`List<ProjectEntity>\`.
  - Item tap triggers \`startActivity(new Intent(context, ProjectDetailsActivity.class).putExtra("project_id", p.getId()))\`.

### Screen 4: Project Details & Associated Milestones (\`ProjectDetailsActivity.java\`)
- **Layout File**: \`activity_project_details.xml\`
- **Core View Elements**:
  - \`btnBackProjectDetails\` (\`ImageButton\`): Top-bar back arrow navigating to previous screen.
  - \`tvProjectTitle\`, \`tvProjectCode\`, \`tvTargetBaselineDate\`: Milestone header metadata.
  - \`rvAssociatedTasks\` (\`RecyclerView\`): Real-time list of tasks specifically belonging to this project.
- **Controller Logic**:
  1. \`onResume()\` triggers \`repository.getTasks(projectId)\` ensuring admin-created web tasks appear instantly.
  2. Subscribes to Room LiveData observing task modifications in background.

### Screen 5: Create Project Task Form (\`CreateTaskActivity.java\`)
- **Layout File**: \`activity_create_task.xml\` (Redesigned with Warm Limestone Mineral Aesthetic)
- **Core View Elements**:
  - \`etTaskTitle\` (\`EditText\`): Milestone title input.
  - \`etTaskDescription\` (\`EditText\`): Detailed acceptance criteria.
  - \`spnPriority\` (\`Spinner\`): Priority selector (LOW, MEDIUM, HIGH, CRITICAL).
  - \`spnAssignee\` (\`Spinner\`): Team member selector dynamically populated from Supabase roster.
  - \`btnSaveTask\` (\`MaterialButton\`): Dispatches task mutation.
- **Controller Logic**:
  - Supports offline write: writes directly to Room SQLite database and enqueues payload in \`sync_queue\`.

### Screen 6: Filterable Tasks Explorer (\`TasksFragment.java\`)
- **Layout File**: \`fragment_tasks.xml\`
- **Core View Elements**:
  - \`searchViewTasks\` (\`SearchView\`): Real-time keyword filter.
  - \`chipGroupStatus\` (\`ChipGroup\`): Status filter chips (All, To Do, In Progress, Done).
  - \`rvTasksFeed\` (\`RecyclerView\`): Dense task cards with story point pills and priority tags.
- **Controller Logic**:
  - Uses \`DiffUtil\` in \`TaskAdapter\` to perform smooth animations on status transitions.

### Screen 7: Deep-Dive Task Details (\`TaskDetailsActivity.java\`)
- **Layout File**: \`activity_task_details.xml\`
- **Core View Elements**:
  - \`sliderProgress\` (\`Slider\`): 0% to 100% completion adjuster.
  - \`btnStatusTodo\`, \`btnStatusInProgress\`, \`btnStatusDone\`: Direct status transition buttons.
  - \`tvAssigneeName\`, \`tvDueDate\`: Assignee card and deadline countdown.

### Screen 8: WhatsApp-Style Messaging Inbox (\`ChatFragment.java\`)
- **Layout File**: \`fragment_chat.xml\`
- **Core View Elements**:
  - \`rvConversationList\` (\`RecyclerView\`): Threads list displaying direct DMs and squad channels.
  - \`layoutActiveChatRoom\` (\`ViewGroup\`): Chat message stream with bubble styling.
  - \`btnChatRoomOptions\` (\`ImageButton\`): 3-dots options button opening contact inspection modal.
  - \`etMessageComposer\` (\`EditText\`): Input box with send button and emoji reaction triggers.

### Screen 9: Direct 1-on-1 Contact Inspection Dialog (\`dialog_contact_details.xml\`)
- **Controller**: Triggered via \`btnChatRoomOptions.setOnClickListener\` inside \`ChatFragment.java\`.
- **View Elements**:
  - User avatar with uppercase initial.
  - Full Name, Corporate Email, and Global Role tag.
  - Presence indicator: \`🟢 Online\` (active within last 3 minutes) or \`⚪ Offline\`.
  - Number of active tasks currently delegated to this teammate.

### Screen 10: Team Roster Directory (\`TeamFragment.java\`)
- **Layout File**: \`fragment_team.xml\`
- **View Elements**:
  - Grid/List of team member cards with role badges and active projects.
  - Clicking any card invokes \`openDirectChatWithMember()\`, immediately opening private chat room.

### Screen 11: Mobile Deterministic Risk Radar (\`RisksFragment.java\`)
- **Layout File**: \`fragment_risks.xml\`
- **View Elements**:
  - Real-time telemetry feed of overdue tasks and resource bottlenecks.
  - "Acknowledge & Mitigate" button resolving risk findings.

### Screen 12: In-App Notifications Drawer (\`NotificationsActivity.java\`)
- **Layout File**: \`activity_notifications.xml\`
- **View Elements**:
  - Chronological stream of system tray alerts, task assignments, and mentions.
  - "Mark All Read" action button.

### Screen 13: Native APK Distribution Portal (\`ShareApkActivity.java\`)
- **Layout File**: \`activity_share_apk.xml\`
- **View Elements**:
  - Displays binary size (8.11 MB) and SHA-256 integrity checksum.
  - "Share via WhatsApp / Nearby" button opening native Android \`Intent.ACTION_SEND\` with \`FileProvider\`.

### Screen 14: User Profile & Preferences (\`ProfileFragment.java\`)
- **Layout File**: \`fragment_profile.xml\`
- **View Elements**:
  - User identity card, email, role badge.
  - "Edit Display Name" custom rounded dialog card.
  - High-contrast white-text "Logout" button with confirmation alert.

### Screen 15: Theme & Offline Settings Dialog
- **Controller**: Embedded in \`ProfileFragment\`.
- **View Elements**:
  - Theme selector: Light Mode (default) / Dark Mode / System Default.
  - Offline sync status indicator displaying pending mutations count in \`sync_queue\`.

### Screen 16: What-If Scheduling Simulation Visualizer
- **Layout File**: \`dialog_whatif_scenario.xml\`
- **View Elements**:
  - Sliders for simulated milestone duration changes.
  - Real-time finish date projection computed via topological DAG engine.
`;

const additionalApiDeepDive = `
---

# 6.1 EXHAUSTIVE REST API ENDPOINT SPECIFICATIONS & PAYLOAD CONTRACTS

Below are detailed payload specifications, sample JSON bodies, and status codes for the core operational APIs.

### 1. \`POST /api/v1/auth/login\`
- **Headers**: \`Content-Type: application/json\`
- **Request Body**:
\`\`\`json
{
  "email": "admin@projectflow.io",
  "password": "ProjectFlow@2026"
}
\`\`\`
- **Response Body (200 OK)**:
\`\`\`json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": "00000000-0000-0000-0000-000000000001",
    "email": "admin@projectflow.io",
    "fullName": "System Administrator",
    "role": "ADMINISTRATOR",
    "active": true
  },
  "message": "Authentication successful"
}
\`\`\`

### 2. \`POST /api/v1/users/fcm-token\`
- **Headers**: \`Authorization: Bearer <TOKEN>\`, \`Content-Type: application/json\`
- **Request Body**:
\`\`\`json
{
  "fcmToken": "f--BtexPSOKsw_1ze9RBFw:APA91bEsk_bdaUnLRa8XxUnYZryjtf4g...",
  "email": "admin@projectflow.io"
}
\`\`\`
- **Response Body (200 OK)**:
\`\`\`json
{
  "success": true,
  "count": 1
}
\`\`\`

### 3. \`POST /api/v1/projects/:id/tasks\`
- **Headers**: \`Authorization: Bearer <TOKEN>\`, \`Content-Type: application/json\`
- **Request Body**:
\`\`\`json
{
  "title": "Deploy Database Indexes",
  "description": "Create B-Tree index on tasks(project_id, due_date)",
  "priority": "HIGH",
  "dueDate": "2026-11-20",
  "assigneeId": "00000000-0000-0000-0000-000000000003",
  "storyPoints": 5
}
\`\`\`
- **Response Body (201 Created)**:
\`\`\`json
{
  "id": "31b209c1-4b12-4fe1-b0e2-76a0d24e1234",
  "projectId": "10000000-0000-0000-0000-000000000001",
  "title": "Deploy Database Indexes",
  "priority": "HIGH",
  "statusCategory": "TODO",
  "progressPercent": 0,
  "storyPoints": 5,
  "dueDate": "2026-11-20",
  "createdAt": "2026-10-17T12:00:00.000Z"
}
\`\`\`

### 4. \`PATCH /api/v1/tasks/:id/status\`
- **Headers**: \`Authorization: Bearer <TOKEN>\`, \`Content-Type: application/json\`
- **Request Body**:
\`\`\`json
{
  "statusCategory": "IN_PROGRESS",
  "progressPercent": 50
}
\`\`\`
- **Response Body (200 OK)**:
\`\`\`json
{
  "id": "31b209c1-4b12-4fe1-b0e2-76a0d24e1234",
  "statusCategory": "IN_PROGRESS",
  "progressPercent": 50,
  "updatedAt": "2026-10-17T12:15:00.000Z"
}
\`\`\`

### 5. \`POST /api/v1/chat/messages\`
- **Headers**: \`Authorization: Bearer <TOKEN>\`, \`Content-Type: application/json\`
- **Request Body**:
\`\`\`json
{
  "channel": "dm_admin_projectflow_io_member_projectflow_io",
  "content": "Please verify the offline sync queue before signing off.",
  "senderName": "System Administrator"
}
\`\`\`
- **Response Body (201 Created)**:
\`\`\`json
{
  "id": "msg_9821034",
  "channel": "dm_admin_projectflow_io_member_projectflow_io",
  "senderName": "System Administrator",
  "content": "Please verify the offline sync queue before signing off.",
  "reactions": {"👍": 0, "❤️": 0, "🚀": 0, "🔥": 0, "🎯": 0},
  "createdAt": "2026-10-17T12:20:00.000Z"
}
\`\`\`

### 6. \`POST /api/v1/broadcast/send\`
- **Headers**: \`Authorization: Bearer <TOKEN>\`, \`Content-Type: application/json\`
- **Request Body**:
\`\`\`json
{
  "title": "Emergency Milestone Shift",
  "message": "All sprint deliverables have been fast-tracked by 48 hours.",
  "type": "BROADCAST_ALERT"
}
\`\`\`
- **Response Body (200 OK)**:
\`\`\`json
{
  "success": true,
  "message": "Dispatched to 1 active mobile subscribers",
  "recipientsCount": 1,
  "timestamp": "2026-10-17T12:25:00.000Z"
}
\`\`\`

### 7. \`GET /api/v1/admin/audit-events?page=0&size=25&action=USER_ROLE_CHANGED\`
- **Headers**: \`Authorization: Bearer <TOKEN>\`
- **Response Body (200 OK)**:
\`\`\`json
{
  "content": [
    {
      "id": "7bbea951-bc82-4c6c-aec8-de4c3eb38638",
      "actorEmail": "admin@projectflow.io",
      "action": "USER_ROLE_CHANGED",
      "entityType": "USER",
      "entityId": "9a5e874c-cffd-4112-84f2-6f9267febc9b",
      "details": "{\"oldRole\":\"MEMBER\",\"newRole\":\"MANAGER\",\"email\":\"newengineer@projectflow.io\"}",
      "timestamp": "2026-10-17T12:16:04.025Z"
    }
  ],
  "totalElements": 1,
  "totalPages": 1,
  "size": 25,
  "number": 0
}
\`\`\`

### 8. \`PATCH /api/v1/admin/settings\`
- **Headers**: \`Authorization: Bearer <TOKEN>\`, \`Content-Type: application/json\`
- **Request Body**:
\`\`\`json
{
  "organizationName": "ProjectFlow Enterprise Systems",
  "syncIntervalMinutes": 15,
  "maxBatchSize": 100,
  "offlineGracePeriodHours": 72,
  "fcmEnabled": true,
  "riskSeverityThreshold": "MEDIUM"
}
\`\`\`
- **Response Body (200 OK)**:
\`\`\`json
{
  "organizationName": "ProjectFlow Enterprise Systems",
  "syncIntervalMinutes": 15,
  "maxBatchSize": 100,
  "offlineGracePeriodHours": 72,
  "fcmEnabled": true,
  "riskSeverityThreshold": "MEDIUM",
  "updatedAt": "2026-10-17T12:30:00.000Z"
}
\`\`\`
`;

const updatedContent = content + additionalScreenDetails + additionalApiDeepDive;
fs.writeFileSync(filePath, updatedContent, 'utf8');
console.log('Successfully expanded bible with detailed screen inventory and full API payload specs!');
