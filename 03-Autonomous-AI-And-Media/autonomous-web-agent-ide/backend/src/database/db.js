const initSqlJs = require('sql.js');
const path = require('path');
const fs = require('fs');

const DB_PATH = process.env.DATABASE_PATH || path.resolve(__dirname, '../../../data/agent.sqlite');

// Ensure data directory exists
const dbDir = path.dirname(DB_PATH);
if (!fs.existsSync(dbDir)) {
  fs.mkdirSync(dbDir, { recursive: true });
}

class SQLiteWrapper {
  constructor(filePath) {
    this.filePath = filePath;
    this.db = null;
    this.lastMtime = 0;
    this.SQLInstance = null;
    this.ready = this.init();
  }

  async init() {
    this.SQLInstance = await initSqlJs();
    this.reloadFromDisk();
    this.initSchema();
    this.persist();
    return this;
  }

  reloadFromDisk() {
    if (!this.SQLInstance) return;
    if (fs.existsSync(this.filePath)) {
      try {
        const stats = fs.statSync(this.filePath);
        if (stats.mtimeMs > this.lastMtime) {
          const fileBuffer = fs.readFileSync(this.filePath);
          if (fileBuffer.length > 0) {
            this.db = new this.SQLInstance.Database(fileBuffer);
            this.lastMtime = stats.mtimeMs;
          }
        }
      } catch (err) {
        console.error('Error reloading SQLite database file:', err);
      }
    }
    if (!this.db) {
      this.db = new this.SQLInstance.Database();
    }
  }

  persist() {
    if (!this.db) return;
    try {
      const data = this.db.export();
      const buffer = Buffer.from(data);
      fs.writeFileSync(this.filePath, buffer);
      if (fs.existsSync(this.filePath)) {
        this.lastMtime = fs.statSync(this.filePath).mtimeMs;
      }
    } catch (err) {
      console.error('Failed to persist SQLite database to disk:', err);
    }
  }

  exec(sql) {
    this.reloadFromDisk();
    if (!this.db) return;
    this.db.exec(sql);
    this.persist();
  }

  prepare(sql) {
    return {
      run: (...params) => {
        this.reloadFromDisk();
        if (!this.db) return { changes: 0, lastInsertRowid: 0 };
        const args = params.length === 1 && Array.isArray(params[0]) ? params[0] : params;
        this.db.run(sql, args);
        this.persist();
        return { changes: 1 };
      },
      all: (...params) => {
        this.reloadFromDisk();
        if (!this.db) return [];
        const args = params.length === 1 && Array.isArray(params[0]) ? params[0] : params;
        const stmt = this.db.prepare(sql);
        stmt.bind(args);
        const results = [];
        while (stmt.step()) {
          results.push(stmt.getAsObject());
        }
        stmt.free();
        return results;
      },
      get: (...params) => {
        this.reloadFromDisk();
        if (!this.db) return null;
        const args = params.length === 1 && Array.isArray(params[0]) ? params[0] : params;
        const stmt = this.db.prepare(sql);
        stmt.bind(args);
        let result = null;
        if (stmt.step()) {
          result = stmt.getAsObject();
        }
        stmt.free();
        return result;
      }
    };
  }

  transaction(fn) {
    return (...args) => {
      this.exec('BEGIN TRANSACTION;');
      try {
        const res = fn(...args);
        this.exec('COMMIT;');
        this.persist();
        return res;
      } catch (err) {
        this.exec('ROLLBACK;');
        throw err;
      }
    };
  }

  initSchema() {
    this.exec(`
      CREATE TABLE IF NOT EXISTS projects (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        path TEXT NOT NULL,
        prompt TEXT,
        status TEXT DEFAULT 'PENDING',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
      );

      CREATE TABLE IF NOT EXISTS agent_runs (
        id TEXT PRIMARY KEY,
        project_id TEXT NOT NULL,
        status TEXT DEFAULT 'PENDING',
        total_iterations INTEGER DEFAULT 0,
        approval_mode TEXT DEFAULT 'SAFE',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        completed_at DATETIME
      );

      CREATE TABLE IF NOT EXISTS tasks (
        id TEXT PRIMARY KEY,
        project_id TEXT NOT NULL,
        run_id TEXT,
        title TEXT NOT NULL,
        description TEXT,
        status TEXT DEFAULT 'PENDING',
        order_index INTEGER NOT NULL DEFAULT 0,
        parent_task_id TEXT,
        retry_count INTEGER DEFAULT 0,
        error_message TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
      );

      CREATE TABLE IF NOT EXISTS task_dependencies (
        id TEXT PRIMARY KEY,
        task_id TEXT NOT NULL,
        depends_on_task_id TEXT NOT NULL
      );

      CREATE TABLE IF NOT EXISTS agent_events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        event_id TEXT UNIQUE NOT NULL,
        project_id TEXT,
        run_id TEXT,
        event_type TEXT NOT NULL,
        payload TEXT NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
      );

      CREATE TABLE IF NOT EXISTS commands (
        id TEXT PRIMARY KEY,
        project_id TEXT NOT NULL,
        run_id TEXT,
        task_id TEXT,
        command TEXT NOT NULL,
        cwd TEXT,
        exit_code INTEGER,
        duration_ms INTEGER,
        stdout TEXT,
        stderr TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
      );

      CREATE TABLE IF NOT EXISTS processes (
        id TEXT PRIMARY KEY,
        project_id TEXT NOT NULL,
        pid INTEGER,
        name TEXT NOT NULL,
        command TEXT NOT NULL,
        cwd TEXT NOT NULL,
        port INTEGER,
        status TEXT DEFAULT 'RUNNING',
        started_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        stopped_at DATETIME
      );

      CREATE TABLE IF NOT EXISTS approvals (
        id TEXT PRIMARY KEY,
        project_id TEXT NOT NULL,
        run_id TEXT,
        action_type TEXT NOT NULL,
        action_payload TEXT NOT NULL,
        status TEXT DEFAULT 'PENDING',
        reason TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        resolved_at DATETIME
      );

      CREATE TABLE IF NOT EXISTS checkpoints (
        id TEXT PRIMARY KEY,
        project_id TEXT NOT NULL,
        task_id TEXT,
        commit_hash TEXT NOT NULL,
        message TEXT NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
      );

      CREATE TABLE IF NOT EXISTS settings (
        key TEXT PRIMARY KEY,
        value TEXT NOT NULL,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
      );
    `);
  }
}

const db = new SQLiteWrapper(DB_PATH);

module.exports = {
  db,
  initSchema: () => db.initSchema()
};
