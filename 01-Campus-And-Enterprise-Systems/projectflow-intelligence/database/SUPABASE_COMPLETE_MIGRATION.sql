-- ==============================================================================
-- PROJECTFLOW INTELLIGENCE — COMPLETE CONSOLIDATED SUPABASE POSTGRESQL MIGRATION
-- Compatible with Supabase PostgreSQL (SQL Editor & psql CLI)
-- Version: 4.0 (Full Product Architecture)
-- ==============================================================================

-- Enable UUID extension if not already enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ------------------------------------------------------------------------------
-- 1. PROFILES (Users)
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.profiles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) NOT NULL UNIQUE,
    full_name VARCHAR(255) NOT NULL,
    avatar_url TEXT,
    global_role VARCHAR(50) NOT NULL DEFAULT 'MEMBER',
    active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ------------------------------------------------------------------------------
-- 2. ORGANIZATIONS
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.organizations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(100) NOT NULL UNIQUE,
    created_by UUID REFERENCES public.profiles(id) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ------------------------------------------------------------------------------
-- 3. ORGANIZATION MEMBERS
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.organization_members (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES public.organizations(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    role VARCHAR(50) NOT NULL DEFAULT 'MEMBER',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_org_member UNIQUE(organization_id, user_id)
);

-- ------------------------------------------------------------------------------
-- 4. WORKSPACES
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.workspaces (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES public.organizations(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(100) NOT NULL,
    description TEXT,
    owner_id UUID REFERENCES public.profiles(id) ON DELETE SET NULL,
    archived BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_workspace_slug UNIQUE(organization_id, slug)
);

-- ------------------------------------------------------------------------------
-- 5. WORKSPACE MEMBERS
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.workspace_members (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    workspace_id UUID NOT NULL REFERENCES public.workspaces(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    role VARCHAR(50) NOT NULL DEFAULT 'MEMBER',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_ws_member UNIQUE(workspace_id, user_id)
);

-- ------------------------------------------------------------------------------
-- 6. WORKFLOWS
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.workflows (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    workspace_id UUID NOT NULL REFERENCES public.workspaces(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    is_default BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ------------------------------------------------------------------------------
-- 7. WORKFLOW STATUSES
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.workflow_statuses (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    workflow_id UUID NOT NULL REFERENCES public.workflows(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    color VARCHAR(50) NOT NULL DEFAULT '#78866B',
    category VARCHAR(50) NOT NULL DEFAULT 'TODO',
    position INT NOT NULL DEFAULT 0,
    CONSTRAINT uq_wf_status_name UNIQUE(workflow_id, name)
);

-- ------------------------------------------------------------------------------
-- 8. WORKFLOW TRANSITIONS
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.workflow_transitions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    workflow_id UUID NOT NULL REFERENCES public.workflows(id) ON DELETE CASCADE,
    from_status_id UUID REFERENCES public.workflow_statuses(id) ON DELETE CASCADE,
    to_status_id UUID NOT NULL REFERENCES public.workflow_statuses(id) ON DELETE CASCADE,
    name VARCHAR(100),
    CONSTRAINT uq_wf_transition UNIQUE(workflow_id, from_status_id, to_status_id)
);

-- ------------------------------------------------------------------------------
-- 9. PROJECTS
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.projects (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    workspace_id UUID NOT NULL REFERENCES public.workspaces(id) ON DELETE CASCADE,
    workflow_id UUID REFERENCES public.workflows(id) ON DELETE SET NULL,
    name VARCHAR(255) NOT NULL,
    code VARCHAR(50) NOT NULL DEFAULT 'PRJ',
    description TEXT,
    start_date DATE NOT NULL,
    target_date DATE NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'ACTIVE',
    health VARCHAR(50) NOT NULL DEFAULT 'ON_TRACK',
    progress_percentage NUMERIC(5,2) NOT NULL DEFAULT 0.00,
    archived BOOLEAN NOT NULL DEFAULT FALSE,
    version BIGINT NOT NULL DEFAULT 1,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_project_dates CHECK (target_date >= start_date)
);

-- ------------------------------------------------------------------------------
-- 10. PROJECT MEMBERS
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.project_members (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID NOT NULL REFERENCES public.projects(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    role VARCHAR(50) NOT NULL DEFAULT 'MEMBER',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_proj_member UNIQUE(project_id, user_id)
);

-- ------------------------------------------------------------------------------
-- 11. TASKS
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.tasks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID NOT NULL REFERENCES public.projects(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    assignee_id UUID REFERENCES public.profiles(id) ON DELETE SET NULL,
    priority VARCHAR(50) NOT NULL DEFAULT 'MEDIUM',
    status_id UUID REFERENCES public.workflow_statuses(id) ON DELETE SET NULL,
    status_category VARCHAR(50) NOT NULL DEFAULT 'TODO',
    due_date DATE,
    estimated_hours NUMERIC(6,2) NOT NULL DEFAULT 0.00,
    progress_percent INT NOT NULL DEFAULT 0,
    position INT NOT NULL DEFAULT 0,
    archived BOOLEAN NOT NULL DEFAULT FALSE,
    version BIGINT NOT NULL DEFAULT 1,
    completed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ------------------------------------------------------------------------------
-- 12. TASK DEPENDENCIES
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.task_dependencies (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    task_id UUID NOT NULL REFERENCES public.tasks(id) ON DELETE CASCADE,
    predecessor_task_id UUID NOT NULL REFERENCES public.tasks(id) ON DELETE CASCADE,
    dependency_type VARCHAR(50) NOT NULL DEFAULT 'FINISH_TO_START',
    CONSTRAINT uq_task_dep UNIQUE(task_id, predecessor_task_id),
    CONSTRAINT chk_no_self_dep CHECK (task_id <> predecessor_task_id)
);

-- ------------------------------------------------------------------------------
-- 13. TASK COMMENTS
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.task_comments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    task_id UUID NOT NULL REFERENCES public.tasks(id) ON DELETE CASCADE,
    author_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ------------------------------------------------------------------------------
-- 14. RISK EVENTS
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.risk_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID NOT NULL REFERENCES public.projects(id) ON DELETE CASCADE,
    rule_id VARCHAR(100) NOT NULL,
    severity VARCHAR(50) NOT NULL,
    affected_entity_type VARCHAR(50) NOT NULL,
    affected_entity_id UUID NOT NULL,
    affected_entity_name VARCHAR(255) NOT NULL,
    explanation TEXT NOT NULL,
    supporting_evidence TEXT NOT NULL,
    suggested_action TEXT NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'ACTIVE',
    detected_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP WITH TIME ZONE
);

-- ------------------------------------------------------------------------------
-- 15. SCHEDULE SCENARIOS
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.schedule_scenarios (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID NOT NULL REFERENCES public.projects(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    created_by_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    applied BOOLEAN NOT NULL DEFAULT FALSE,
    applied_at TIMESTAMP WITH TIME ZONE,
    base_project_version BIGINT NOT NULL DEFAULT 1,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ------------------------------------------------------------------------------
-- 16. SCENARIO CHANGES
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.scenario_changes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    scenario_id UUID NOT NULL REFERENCES public.schedule_scenarios(id) ON DELETE CASCADE,
    task_id UUID NOT NULL REFERENCES public.tasks(id) ON DELETE CASCADE,
    proposed_due_date DATE,
    proposed_estimated_hours NUMERIC(6,2),
    proposed_assignee_id UUID REFERENCES public.profiles(id) ON DELETE SET NULL
);

-- ------------------------------------------------------------------------------
-- 17. SYNC OPERATIONS (Idempotent Offline Queue)
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.sync_operations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    client_operation_id VARCHAR(128) NOT NULL UNIQUE,
    entity_type VARCHAR(50) NOT NULL,
    entity_id UUID NOT NULL,
    operation_type VARCHAR(50) NOT NULL,
    payload_json TEXT NOT NULL,
    base_version BIGINT NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'PENDING',
    error_message TEXT,
    client_created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    processed_at TIMESTAMP WITH TIME ZONE
);

-- ------------------------------------------------------------------------------
-- 18. AUDIT LOGS
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID,
    workspace_id UUID,
    actor_id UUID,
    actor_email VARCHAR(255),
    action VARCHAR(100) NOT NULL,
    entity_type VARCHAR(50) NOT NULL,
    entity_id UUID,
    details TEXT,
    ip_address VARCHAR(100),
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ------------------------------------------------------------------------------
-- 19. AUTOMATION RULES
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.automation_rules (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    workspace_id UUID NOT NULL REFERENCES public.workspaces(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    trigger_type VARCHAR(100) NOT NULL,
    trigger_config TEXT DEFAULT '{}',
    action_type VARCHAR(100) NOT NULL,
    action_config TEXT DEFAULT '{}',
    active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ------------------------------------------------------------------------------
-- 20. APP RELEASES (Binary Distribution & Hash Verification)
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.app_releases (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    application_id VARCHAR(100) NOT NULL DEFAULT 'com.projectflow.android',
    version_name VARCHAR(50) NOT NULL,
    version_code BIGINT NOT NULL,
    artifact_filename VARCHAR(255) NOT NULL,
    storage_path TEXT NOT NULL,
    mime_type VARCHAR(100) NOT NULL DEFAULT 'application/vnd.android.package-archive',
    file_size_bytes BIGINT NOT NULL,
    sha256_checksum VARCHAR(64) NOT NULL,
    release_channel VARCHAR(50) NOT NULL DEFAULT 'STABLE',
    release_notes TEXT,
    minimum_supported_version_code BIGINT DEFAULT 1,
    status VARCHAR(50) NOT NULL DEFAULT 'PUBLISHED',
    created_by UUID REFERENCES public.profiles(id) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    published_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_app_version UNIQUE (application_id, version_code),
    CONSTRAINT chk_release_status CHECK (status IN ('DRAFT', 'PUBLISHED', 'ARCHIVED', 'DEPRECATED')),
    CONSTRAINT chk_release_channel CHECK (release_channel IN ('STABLE', 'BETA', 'NIGHTLY'))
);

-- ------------------------------------------------------------------------------
-- 21. ERROR LOGS (Telemetry & Persistent Failure Diagnostics)
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.error_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    severity VARCHAR(50) NOT NULL DEFAULT 'ERROR',
    message TEXT NOT NULL,
    stack TEXT,
    source VARCHAR(100) NOT NULL DEFAULT 'ANDROID_APP',
    user_id UUID REFERENCES public.profiles(id) ON DELETE SET NULL,
    metadata JSONB DEFAULT '{}'::jsonb,
    resolved BOOLEAN NOT NULL DEFAULT FALSE,
    resolved_at TIMESTAMP WITH TIME ZONE,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ------------------------------------------------------------------------------
-- 22. CHAT MESSAGES
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.chat_messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    workspace_id UUID REFERENCES public.workspaces(id) ON DELETE CASCADE,
    sender_id UUID REFERENCES public.profiles(id) ON DELETE SET NULL,
    sender_name VARCHAR(255) NOT NULL,
    channel VARCHAR(100) NOT NULL DEFAULT 'general',
    content TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ------------------------------------------------------------------------------
-- 23. NOTIFICATIONS
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.notifications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES public.profiles(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    type VARCHAR(50) NOT NULL DEFAULT 'SYSTEM',
    read BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ==============================================================================
-- INDEXES
-- ==============================================================================
CREATE INDEX IF NOT EXISTS idx_workspaces_org ON public.workspaces(organization_id);
CREATE INDEX IF NOT EXISTS idx_projects_workspace ON public.projects(workspace_id);
CREATE INDEX IF NOT EXISTS idx_tasks_project ON public.tasks(project_id);
CREATE INDEX IF NOT EXISTS idx_tasks_assignee ON public.tasks(assignee_id);
CREATE INDEX IF NOT EXISTS idx_tasks_status ON public.tasks(status_id);
CREATE INDEX IF NOT EXISTS idx_risk_events_project ON public.risk_events(project_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_org_time ON public.audit_logs(organization_id, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_sync_client_op ON public.sync_operations(client_operation_id);
CREATE INDEX IF NOT EXISTS idx_releases_app_status ON public.app_releases(application_id, status);
CREATE INDEX IF NOT EXISTS idx_releases_published_at ON public.app_releases(published_at DESC);
CREATE INDEX IF NOT EXISTS idx_error_logs_severity ON public.error_logs(severity, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_chat_messages_channel ON public.chat_messages(channel, created_at ASC);
CREATE INDEX IF NOT EXISTS idx_notifications_user ON public.notifications(user_id, read);

-- ==============================================================================
-- ROW LEVEL SECURITY (RLS) POLICIES
-- ==============================================================================
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.organizations ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.organization_members ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.workspaces ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.workspace_members ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.workflows ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.workflow_statuses ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.workflow_transitions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.projects ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.project_members ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.tasks ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.task_dependencies ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.task_comments ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.risk_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.schedule_scenarios ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.scenario_changes ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.sync_operations ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.audit_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.automation_rules ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.app_releases ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.error_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.chat_messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.notifications ENABLE ROW LEVEL SECURITY;

-- Allow read/write access for authenticated and anon users (for dev & service keys)
DO $$
DECLARE
    tbl text;
BEGIN
    FOR tbl IN 
        SELECT tablename FROM pg_tables WHERE schemaname = 'public'
    LOOP
        EXECUTE format('DROP POLICY IF EXISTS "Public access on %I" ON public.%I', tbl, tbl);
        EXECUTE format('CREATE POLICY "Public access on %I" ON public.%I FOR ALL USING (true) WITH CHECK (true)', tbl, tbl);
    END LOOP;
END $$;

-- ==============================================================================
-- INITIAL SEED DATA (Idempotent ON CONFLICT DO NOTHING)
-- ==============================================================================

-- 1. Profiles
INSERT INTO public.profiles (id, email, full_name, global_role, active)
VALUES 
    ('00000000-0000-0000-0000-000000000001', 'admin@projectflow.io', 'System Administrator', 'ADMINISTRATOR', TRUE),
    ('00000000-0000-0000-0000-000000000002', 'manager@projectflow.io', 'Project Manager', 'MANAGER', TRUE),
    ('00000000-0000-0000-0000-000000000003', 'member@projectflow.io', 'Team Member', 'MEMBER', TRUE)
ON CONFLICT (id) DO NOTHING;

-- 2. Organization
INSERT INTO public.organizations (id, name, slug, created_by)
VALUES 
    ('00000000-0000-0000-0000-000000000001', 'ProjectFlow HQ', 'projectflow-hq', '00000000-0000-0000-0000-000000000001')
ON CONFLICT (id) DO NOTHING;

-- 3. Workspace
INSERT INTO public.workspaces (id, organization_id, name, slug, description, owner_id)
VALUES 
    ('00000000-0000-0000-0000-000000000001', '00000000-0000-0000-0000-000000000001', 'Engineering & Innovation', 'engineering-innovation', 'Core product development workspace domain.', '00000000-0000-0000-0000-000000000001')
ON CONFLICT (id) DO NOTHING;

-- 4. Workflow & Statuses
INSERT INTO public.workflows (id, workspace_id, name, description, is_default)
VALUES 
    ('00000000-0000-0000-0000-000000000001', '00000000-0000-0000-0000-000000000001', 'Standard Agile Workflow', 'Default flow: To Do -> In Progress -> Review -> Done', TRUE)
ON CONFLICT (id) DO NOTHING;

INSERT INTO public.workflow_statuses (id, workflow_id, name, color, category, position)
VALUES 
    ('00000000-0000-0000-0000-000000000011', '00000000-0000-0000-0000-000000000001', 'To Do', '#78866B', 'TODO', 0),
    ('00000000-0000-0000-0000-000000000012', '00000000-0000-0000-0000-000000000001', 'In Progress', '#56664C', 'IN_PROGRESS', 1),
    ('00000000-0000-0000-0000-000000000013', '00000000-0000-0000-0000-000000000001', 'In Review', '#8A9A5B', 'IN_PROGRESS', 2),
    ('00000000-0000-0000-0000-000000000014', '00000000-0000-0000-0000-000000000001', 'Done', '#467653', 'DONE', 3)
ON CONFLICT (id) DO NOTHING;

-- 5. Project
INSERT INTO public.projects (id, workspace_id, workflow_id, name, code, description, start_date, target_date, status, health, progress_percentage)
VALUES 
    ('10000000-0000-0000-0000-000000000001', '00000000-0000-0000-0000-000000000001', '00000000-0000-0000-0000-000000000001', 'ProjectFlow Core Platform', 'PF-CORE', 'Full-stack cross-platform intelligence application.', CURRENT_DATE, CURRENT_DATE + INTERVAL '30 days', 'ACTIVE', 'ON_TRACK', 65.00)
ON CONFLICT (id) DO NOTHING;

-- 6. Tasks
INSERT INTO public.tasks (id, project_id, title, description, assignee_id, priority, status_id, status_category, due_date, estimated_hours, progress_percent, completed_at)
VALUES 
    ('20000000-0000-0000-0000-000000000001', '10000000-0000-0000-0000-000000000001', 'Database & API Architecture', 'Setup Supabase tables, REST endpoints, and security policies.', '00000000-0000-0000-0000-000000000001', 'CRITICAL', '00000000-0000-0000-0000-000000000014', 'DONE', CURRENT_DATE - INTERVAL '2 days', 16.00, 100, CURRENT_TIMESTAMP),
    ('20000000-0000-0000-0000-000000000002', '10000000-0000-0000-0000-000000000001', 'Frontend Admin Panel & Telemetry', 'React 18 Natural Mineral dashboard with live metrics and logo branding.', '00000000-0000-0000-0000-000000000002', 'HIGH', '00000000-0000-0000-0000-000000000012', 'IN_PROGRESS', CURRENT_DATE + INTERVAL '2 days', 24.00, 85, NULL),
    ('20000000-0000-0000-0000-000000000003', '10000000-0000-0000-0000-000000000001', 'Deterministic Risk Radar Engine', 'Implement 6 mathematical risk rules in JavaScript.', '00000000-0000-0000-0000-000000000003', 'HIGH', '00000000-0000-0000-0000-000000000012', 'IN_PROGRESS', CURRENT_DATE + INTERVAL '5 days', 20.00, 90, NULL)
ON CONFLICT (id) DO NOTHING;

-- 7. Task Dependencies
INSERT INTO public.task_dependencies (id, task_id, predecessor_task_id, dependency_type)
VALUES 
    ('30000000-0000-0000-0000-000000000001', '20000000-0000-0000-0000-000000000002', '20000000-0000-0000-0000-000000000001', 'FINISH_TO_START')
ON CONFLICT (id) DO NOTHING;

-- 8. App Release
INSERT INTO public.app_releases (
    id, application_id, version_name, version_code, artifact_filename, storage_path, 
    mime_type, file_size_bytes, sha256_checksum, release_channel, release_notes, 
    minimum_supported_version_code, status, created_by
)
VALUES (
    '50000000-0000-0000-0000-000000000001',
    'com.projectflow.android',
    '2.0.0',
    200,
    'ProjectFlow-Intelligence-v2.0.0.apk',
    'releases/android/ProjectFlow-Intelligence-v2.0.0.apk',
    'application/vnd.android.package-archive',
    8114674,
    '8c20000160064c7bb80af8765f912ed1d9bb20ef6bffbb4d35ed2b3729030409',
    'STABLE',
    'Official universal signed release of ProjectFlow Intelligence with 16-screen UI flow, Natural Mineral design system, and deterministic risk engine.',
    1,
    'PUBLISHED',
    '00000000-0000-0000-0000-000000000001'
)
ON CONFLICT (application_id, version_code) DO NOTHING;

-- 9. Audit Log
INSERT INTO public.audit_logs (id, workspace_id, actor_id, actor_email, action, entity_type, details)
VALUES 
    ('40000000-0000-0000-0000-000000000001', '00000000-0000-0000-0000-000000000001', '00000000-0000-0000-0000-000000000001', 'admin@projectflow.io', 'SCHEMA_MIGRATION', 'DATABASE', 'Applied complete consolidated PostgreSQL schema migration v4.0')
ON CONFLICT (id) DO NOTHING;
