-- AURA Database Schema (SQLite)

CREATE TABLE IF NOT EXISTS goals (
    goal_id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    status TEXT NOT NULL DEFAULT 'pending', -- pending, in_progress, completed, failed
    priority INTEGER DEFAULT 1,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS tasks (
    task_id TEXT PRIMARY KEY,
    goal_id TEXT,
    title TEXT NOT NULL,
    description TEXT,
    status TEXT NOT NULL DEFAULT 'pending', -- pending, in_progress, completed, failed
    priority INTEGER DEFAULT 1,
    retry_count INTEGER DEFAULT 0,
    result TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    FOREIGN KEY(goal_id) REFERENCES goals(goal_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS knowledge (
    id TEXT PRIMARY KEY,
    topic TEXT NOT NULL,
    content TEXT NOT NULL,
    source TEXT,
    confidence REAL DEFAULT 1.0,
    embedding TEXT, -- JSON stored embedding vector
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS knowledge_relations (
    id TEXT PRIMARY KEY,
    subject TEXT NOT NULL,
    predicate TEXT NOT NULL, -- e.g. 'requires', 'has_subtopic', 'part_of'
    object TEXT NOT NULL,
    confidence REAL DEFAULT 1.0,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS sources (
    id TEXT PRIMARY KEY,
    url_or_title TEXT NOT NULL,
    type TEXT,
    summary TEXT,
    confidence REAL DEFAULT 1.0,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS experiences (
    id TEXT PRIMARY KEY,
    task_id TEXT,
    goal TEXT,
    result TEXT,
    cause TEXT,
    fix TEXT,
    lesson TEXT,
    embedding TEXT, -- JSON stored embedding vector
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS procedures (
    id TEXT PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    description TEXT,
    steps TEXT NOT NULL, -- JSON array of steps
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS experiments (
    experiment_id TEXT PRIMARY KEY,
    goal TEXT NOT NULL,
    hypothesis TEXT,
    method TEXT,
    code TEXT,
    input TEXT,
    output TEXT,
    result TEXT, -- PASS, FAIL, ERROR
    error TEXT,
    solution TEXT,
    lesson TEXT,
    confidence REAL DEFAULT 0.5,
    timestamp TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS skills (
    id TEXT PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    theoretical_level TEXT DEFAULT 'low', -- low, medium, high
    practical_level TEXT DEFAULT 'low',   -- low, medium, high
    last_used TEXT
);

CREATE TABLE IF NOT EXISTS errors (
    id TEXT PRIMARY KEY,
    error_type TEXT NOT NULL,
    message TEXT NOT NULL,
    context TEXT,
    resolved INTEGER DEFAULT 0,
    resolution TEXT,
    timestamp TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS decisions (
    id TEXT PRIMARY KEY,
    task_id TEXT,
    reasoning TEXT,
    choice TEXT,
    options TEXT,
    timestamp TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS actions (
    id TEXT PRIMARY KEY,
    task_id TEXT,
    tool_name TEXT NOT NULL,
    tool_input TEXT,
    tool_output TEXT,
    status TEXT NOT NULL, -- success, failure, timeout
    timestamp TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS sessions (
    session_id TEXT PRIMARY KEY,
    start_time TEXT NOT NULL,
    end_time TEXT,
    status TEXT DEFAULT 'active'
);

CREATE TABLE IF NOT EXISTS projects (
    project_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    path TEXT NOT NULL,
    status TEXT DEFAULT 'active'
);

CREATE TABLE IF NOT EXISTS learning_sessions (
    id TEXT PRIMARY KEY,
    topic TEXT NOT NULL,
    duration INTEGER DEFAULT 0,
    summary TEXT,
    timestamp TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS knowledge_gaps (
    id TEXT PRIMARY KEY,
    topic TEXT NOT NULL,
    rationale TEXT,
    priority INTEGER DEFAULT 1,
    status TEXT DEFAULT 'open' -- open, researching, resolved
);
