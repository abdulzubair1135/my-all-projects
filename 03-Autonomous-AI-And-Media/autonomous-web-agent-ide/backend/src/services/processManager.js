const { spawn, execSync } = require('child_process');
const { v4: uuidv4 } = require('uuid');
const { db } = require('../database/db');
const eventBus = require('./eventBus');

const PORT_REGEX = /(?:localhost|127\.0\.0\.1|0\.0\.0\.0|port)[:\s]+([0-9]{3,5})/i;

class ProcessManager {
  constructor() {
    this.activeProcesses = new Map(); // id -> child_process instance
  }

  startProcess(projectId, name, command, args = [], cwd, env = {}) {
    const id = uuidv4();
    const isWindows = process.platform === 'win32';
    const shell = isWindows ? 'powershell.exe' : '/bin/bash';
    const fullCommandLine = args.length > 0 ? `${command} ${args.join(' ')}` : command;

    const child = spawn(fullCommandLine, [], {
      cwd,
      shell: true,
      env: { ...process.env, ...env, FORCE_COLOR: '1' }
    });

    const now = new Date().toISOString();
    const procInfo = {
      id,
      project_id: projectId,
      pid: child.pid,
      name,
      command: fullCommandLine,
      cwd,
      port: null,
      status: 'RUNNING',
      started_at: now,
      stopped_at: null
    };

    const stmt = db.prepare(`
      INSERT INTO processes (id, project_id, pid, name, command, cwd, port, status, started_at)
      VALUES (?, ?, ?, ?, ?, ?, ?, 'RUNNING', ?)
    `);
    stmt.run(id, projectId, child.pid, name, fullCommandLine, cwd, null, now);

    this.activeProcesses.set(id, { child, info: procInfo });
    eventBus.emit('process.started', procInfo, projectId);

    child.stdout.on('data', (data) => {
      const text = data.toString();
      
      // Auto-detect server port
      const match = text.match(PORT_REGEX);
      if (match && match[1] && !procInfo.port) {
        procInfo.port = parseInt(match[1], 10);
        db.prepare('UPDATE processes SET port = ? WHERE id = ?').run(procInfo.port, id);
        eventBus.emit('process.updated', procInfo, projectId);
      }

      eventBus.emit('command.output', {
        processId: id,
        name,
        stream: 'stdout',
        data: text
      }, projectId);
    });

    child.stderr.on('data', (data) => {
      const text = data.toString();
      eventBus.emit('command.output', {
        processId: id,
        name,
        stream: 'stderr',
        data: text
      }, projectId);
    });

    child.on('close', (code) => {
      procInfo.status = code === 0 ? 'STOPPED' : 'CRASHED';
      procInfo.stopped_at = new Date().toISOString();
      this.activeProcesses.delete(id);

      db.prepare('UPDATE processes SET status = ?, stopped_at = ? WHERE id = ?')
        .run(procInfo.status, procInfo.stopped_at, id);

      eventBus.emit(code === 0 ? 'process.stopped' : 'process.crashed', {
        ...procInfo,
        exit_code: code
      }, projectId);
    });

    child.on('error', (err) => {
      console.error(`Process error [${name}]:`, err);
      procInfo.status = 'CRASHED';
      procInfo.stopped_at = new Date().toISOString();
      this.activeProcesses.delete(id);

      db.prepare('UPDATE processes SET status = ?, stopped_at = ? WHERE id = ?')
        .run('CRASHED', procInfo.stopped_at, id);

      eventBus.emit('process.crashed', {
        ...procInfo,
        error: err.message
      }, projectId);
    });

    return procInfo;
  }

  stopProcess(id) {
    const item = this.activeProcesses.get(id);
    if (!item) {
      // Check database to update state if stale
      db.prepare("UPDATE processes SET status = 'STOPPED', stopped_at = CURRENT_TIMESTAMP WHERE id = ?").run(id);
      return false;
    }

    const { child, info } = item;
    const isWindows = process.platform === 'win32';

    try {
      if (isWindows) {
        execSync(`taskkill /PID ${child.pid} /T /F`);
      } else {
        process.kill(-child.pid, 'SIGKILL');
      }
    } catch {
      try {
        child.kill('SIGKILL');
      } catch (err) {
        console.error(`Failed to kill process ${child.pid}:`, err);
      }
    }

    info.status = 'STOPPED';
    info.stopped_at = new Date().toISOString();
    this.activeProcesses.delete(id);

    db.prepare('UPDATE processes SET status = ?, stopped_at = ? WHERE id = ?')
      .run('STOPPED', info.stopped_at, id);

    eventBus.emit('process.stopped', info, info.project_id);
    return true;
  }

  listProcesses(projectId = null) {
    if (projectId) {
      return db.prepare('SELECT * FROM processes WHERE project_id = ? ORDER BY started_at DESC').all(projectId);
    }
    return db.prepare('SELECT * FROM processes ORDER BY started_at DESC').all();
  }

  getProcess(id) {
    return db.prepare('SELECT * FROM processes WHERE id = ?').get(id);
  }

  stopAllForProject(projectId) {
    const active = [...this.activeProcesses.entries()].filter(([_, item]) => item.info.project_id === projectId);
    for (const [id] of active) {
      this.stopProcess(id);
    }
  }

  cleanupAll() {
    for (const [id] of this.activeProcesses.keys()) {
      this.stopProcess(id);
    }
  }
}

module.exports = new ProcessManager();
