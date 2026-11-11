# Web Admin Control Panel Guide

The **ProjectFlow Web Admin Control Panel** is an administrative console built with React 18, TypeScript, Vite, and Tailwind CSS, following the Natural Mineral Design System.

---

## Technical Stack
- **Framework**: React 18 with TypeScript 5
- **Build Tool**: Vite 5
- **Routing**: React Router v6
- **Icons**: `lucide-react` (Strictly NO emojis used as UI icons)
- **Styling**: Tailwind CSS configured with Natural Mineral tokens

---

## Functional Console Modules

1. **Dashboard (`/`)**: Real-time aggregate telemetry (Total Users, Workspaces, Projects, Tasks, Active Risks, System Health). Contains graceful empty-state handling if the database is clean.
2. **Workspaces (`/workspaces`)**: Tenant workspace cards, slug management, and modal creation form.
3. **Projects (`/projects`)**: Cross-workspace project directory with status badges and health tags.
4. **Task Explorer (`/tasks`)**: Cross-project task grid with priority filters, progress bars, and creation modal.
5. **Risk Radar (`/risks`)**: Multi-rule breakdown strip, critical findings inspector, and manual rule execution trigger.
6. **User Management (`/users`)**: Searchable user directory with role assignment modal (Admin, Manager, Member, Viewer).
7. **Audit Logs (`/audit-logs`)**: Security event log viewer with JSON payload inspector and pagination.
8. **System Health (`/health`)**: Real-time probe reporting database latency, JVM heap usage, active thread count, and Flyway migration status.
9. **Settings (`/settings`)**: Global tenant isolation policy, periodic sync intervals, and persistence dialect overview.

---

## Running the Web Admin Panel
```bat
cd P:\admin-panel
npm run dev
```
Accessible at `http://localhost:5173`.
