const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');
const { v4: uuidv4 } = require('uuid');
const { db } = require('../database/db');
const eventBus = require('./eventBus');
const projectService = require('./projectService');

const AGENT_DIR = path.resolve(__dirname, '../../../agent');

class AgentBridge {
  constructor() {
    this.currentAgentProcess = null;
    this.activeRunId = null;
    this.activeProjectId = null;
    this.status = 'IDLE';
    this.approvalMode = 'SAFE';
  }

  getStatus() {
    return {
      status: this.status,
      activeRunId: this.activeRunId,
      activeProjectId: this.activeProjectId,
      approvalMode: this.approvalMode
    };
  }

  setApprovalMode(mode) {
    if (['AUTO', 'SAFE', 'ASK'].includes(mode)) {
      this.approvalMode = mode;
      eventBus.emit('settings.updated', { approvalMode: mode }, this.activeProjectId);
    }
  }

  startAgent(projectId, prompt, options = {}) {
    const project = projectService.getProject(projectId);
    if (!project) throw new Error('Project not found');

    if (this.currentAgentProcess) {
      try {
        this.currentAgentProcess.kill('SIGKILL');
      } catch {}
      this.currentAgentProcess = null;
    }

    const runId = uuidv4();
    this.activeRunId = runId;
    this.activeProjectId = projectId;
    this.status = 'RUNNING';
    this.approvalMode = options.approvalMode || this.approvalMode;

    const now = new Date().toISOString();
    db.prepare(`
      INSERT INTO agent_runs (id, project_id, status, approval_mode, created_at)
      VALUES (?, ?, 'RUNNING', ?, ?)
    `).run(runId, projectId, this.approvalMode, now);

    projectService.updateProjectStatus(projectId, 'RUNNING');
    eventBus.emit('agent.started', { runId, projectId, prompt, mode: this.approvalMode }, projectId, runId);

    const isWindows = process.platform === 'win32';
    let pythonBin = isWindows ? 'python' : 'python3';
    const venvPythonWin = path.join(AGENT_DIR, '.venv', 'Scripts', 'python.exe');
    const venvPythonNix = path.join(AGENT_DIR, '.venv', 'bin', 'python');

    if (isWindows && fs.existsSync(venvPythonWin)) {
      pythonBin = venvPythonWin;
    } else if (!isWindows && fs.existsSync(venvPythonNix)) {
      pythonBin = venvPythonNix;
    }

    const provider = options.provider || process.env.DEFAULT_LLM_PROVIDER || 'deepseek_web';
    const agentMain = path.join(AGENT_DIR, 'main.py');
    console.log(`[AgentBridge] Launching agent with Provider: ${provider}`);

    // Image paths attached by user
    const imagePaths = (options.imagePaths || []).filter(Boolean);

    eventBus.emit('command.output', {
      runId,
      name: 'agent',
      stream: 'stdout',
      data: `\r\n\x1b[1;36m🌐 [Selected AI Engine: ${provider.toUpperCase()}]\x1b[0m\r\n`
    }, projectId, runId);

    if (imagePaths.length > 0) {
      eventBus.emit('command.output', {
        runId, name: 'agent', stream: 'stdout',
        data: `📎 [Attachments] ${imagePaths.length} image(s) queued for AI\r\n`
      }, projectId, runId);
    }

    const args = [
      agentMain,
      '--project-id', projectId,
      '--run-id', runId,
      '--project-path', project.path,
      '--prompt', prompt,
      '--provider', provider,
      '--approval-mode', this.approvalMode,
    ];

    // Pass image paths if any
    if (imagePaths.length > 0) {
      args.push('--images', imagePaths.join(','));
    }

    try {
      this.currentAgentProcess = spawn(pythonBin, args, {
        cwd: AGENT_DIR,
        env: {
          ...process.env,
          PYTHONUNBUFFERED: '1',
          DATABASE_PATH: process.env.DATABASE_PATH || path.resolve(__dirname, '../../../data/agent.sqlite'),
          PROJECT_ID: projectId,
          RUN_ID: runId
        }
      });

      this.currentAgentProcess.stdout.on('data', (data) => {
        const text = data.toString();
        const lines = text.split('\n');
        const nonIpcLines = [];

        for (const line of lines) {
          const trimmed = line.trim();
          if (trimmed.startsWith('IPC:JSON:')) {
            try {
              const msg = JSON.parse(trimmed.substring(9));
              this.handleIpcMessage(msg);
            } catch (e) {
              console.error('Error parsing IPC JSON:', e);
            }
          } else if (trimmed) {
            nonIpcLines.push(line);
          }
        }

        if (nonIpcLines.length > 0) {
          eventBus.emit('command.output', {
            runId,
            name: 'agent',
            stream: 'stdout',
            data: nonIpcLines.join('\n') + '\n'
          }, projectId, runId);
        }
      });

      this.currentAgentProcess.stderr.on('data', (data) => {
        const text = data.toString();
        eventBus.emit('command.output', {
          runId,
          name: 'agent',
          stream: 'stderr',
          data: text
        }, projectId, runId);
      });

      this.currentAgentProcess.on('close', (code) => {
        const finalStatus = code === 0 ? 'COMPLETED' : (this.status === 'STOPPED' ? 'STOPPED' : 'FAILED');
        this.status = finalStatus;
        this.currentAgentProcess = null;

        const completedAt = new Date().toISOString();
        db.prepare('UPDATE agent_runs SET status = ?, completed_at = ? WHERE id = ?')
          .run(finalStatus, completedAt, runId);

        projectService.updateProjectStatus(projectId, finalStatus);
        eventBus.emit(code === 0 ? 'agent.completed' : 'agent.stopped', { runId, projectId, code, status: finalStatus }, projectId, runId);
      });

      this.currentAgentProcess.on('error', (err) => {
        console.error('Agent process execution error:', err);
        this.status = 'FAILED';
        this.currentAgentProcess = null;
        eventBus.emit('agent.error', { runId, projectId, error: err.message }, projectId, runId);
      });

      return { runId, projectId, status: 'RUNNING' };
    } catch (err) {
      this.status = 'FAILED';
      this.currentAgentProcess = null;
      throw err;
    }
  }

  handleIpcMessage(msg) {
    if (!msg.event) return;

    const projectId = msg.project_id || this.activeProjectId;
    const runId = msg.run_id || this.activeRunId;
    const payload = msg.payload || {};

    // Sync task state into backend DB if task event
    if (msg.event === 'task.created' && Array.isArray(payload.tasks)) {
      console.log(`[Agent: Plan] Generated ${payload.tasks.length} tasks in task graph.`);
      const now = new Date().toISOString();
      for (const t of payload.tasks) {
        db.prepare(`
          INSERT OR REPLACE INTO tasks (id, project_id, run_id, title, description, status, order_index, retry_count, error_message, updated_at)
          VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        `).run(t.id, projectId, runId, t.title, t.description, t.status, t.order_index, t.retry_count || 0, t.error_message || null, now);
      }
    } else if (msg.event === 'task.started' && payload.id) {
      console.log(`[Agent: Task Started] #${payload.order_index + 1}: ${payload.title}`);
      eventBus.emit('command.output', {
        runId,
        name: 'agent',
        stream: 'stdout',
        data: `\r\n\x1b[1;36m▶ [Task Started] #${(payload.order_index || 0) + 1}: ${payload.title}\x1b[0m\r\n`
      }, projectId, runId);
      db.prepare('UPDATE tasks SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?')
        .run('RUNNING', payload.id);
    } else if (msg.event === 'task.completed' && payload.id) {
      console.log(`[Agent: Task Completed] ${payload.title}`);
      eventBus.emit('command.output', {
        runId,
        name: 'agent',
        stream: 'stdout',
        data: `\x1b[1;32m✔ [Task Completed] ${payload.title}\x1b[0m\r\n`
      }, projectId, runId);
      db.prepare('UPDATE tasks SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?')
        .run('COMPLETED', payload.id);
    } else if (msg.event === 'task.failed' && payload.id) {
      console.log(`[Agent: Task Failed] ${payload.title}`);
      eventBus.emit('command.output', {
        runId,
        name: 'agent',
        stream: 'stderr',
        data: `\x1b[1;31m✖ [Task Failed] ${payload.title}: ${payload.error_message || ''}\x1b[0m\r\n`
      }, projectId, runId);
      db.prepare('UPDATE tasks SET status = ?, error_message = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?')
        .run('FAILED', payload.error_message || 'Task failed', payload.id);
    } else if (msg.event === 'file.created') {
      console.log(`[Agent: File Created] ${payload.path}`);
      eventBus.emit('command.output', {
        runId,
        name: 'agent',
        stream: 'stdout',
        data: `\x1b[34m📄 [File Created] ${payload.path}\x1b[0m\r\n`
      }, projectId, runId);
    } else if (msg.event === 'file.modified') {
      console.log(`[Agent: File Modified] ${payload.path}`);
      eventBus.emit('command.output', {
        runId,
        name: 'agent',
        stream: 'stdout',
        data: `\x1b[33m📝 [File Modified] ${payload.path}\x1b[0m\r\n`
      }, projectId, runId);
    } else if (msg.event === 'score.updated') {
      console.log(`[Agent: Quality Score] ${payload.score} pts (Delta: ${payload.delta >= 0 ? '+' : ''}${payload.delta})`);
      const deltaStr = payload.delta >= 0 ? `+${payload.delta}` : `${payload.delta}`;
      eventBus.emit('command.output', {
        runId,
        name: 'agent',
        stream: 'stdout',
        data: `\x1b[1;33m🏆 [Quality Score Updated] ${payload.score} pts (${deltaStr})\x1b[0m\r\n`
      }, projectId, runId);
    } else if (msg.event === 'agent.role.started') {
      console.log(`[Multi-Agent Role] ${payload.role}: ${payload.message || ''}`);
      eventBus.emit('command.output', {
        runId,
        name: 'agent',
        stream: 'stdout',
        data: `\x1b[1;36m🤖 [Active Agent: ${payload.role}]\x1b[0m ${payload.message || ''}\r\n`
      }, projectId, runId);
    } else if (msg.event === 'preview.open' || msg.event === 'agent.completed') {
      try {
        const processManager = require('./processManager');
        const proj = projectService.getProject(projectId);
        const targetPort = payload?.port || 5174;
        if (proj && (fs.existsSync(path.join(proj.path, 'package.json')) || fs.existsSync(path.join(proj.path, 'client', 'package.json')))) {
          const hasServer = Array.from(processManager.activeProcesses.values()).some(
            p => p.info.project_id === projectId && p.info.status === 'RUNNING'
          );
          if (!hasServer) {
            let targetCwd = proj.path;
            if (fs.existsSync(path.join(proj.path, 'client', 'package.json'))) {
              targetCwd = path.join(proj.path, 'client');
            }
            console.log(`[Auto-Dev-Server] Launching live Vite dev server for ${projectId} on port ${targetPort} in ${targetCwd}...`);
            processManager.startProcess(projectId, 'Vite Dev Server', 'npx', ['vite', '--port', String(targetPort), '--host'], targetCwd);
          }
        }
      } catch (err) {
        console.error('[Auto-Dev-Server Notice]:', err.message);
      }
    }

    eventBus.emit(msg.event, payload, projectId, runId);
  }

  pauseAgent() {
    if (this.currentAgentProcess && this.status === 'RUNNING') {
      this.status = 'PAUSED';
      this.sendIpcCommand({ command: 'pause' });
      eventBus.emit('agent.paused', { runId: this.activeRunId }, this.activeProjectId, this.activeRunId);
      return true;
    }
    return false;
  }

  resumeAgent() {
    if (this.currentAgentProcess && this.status === 'PAUSED') {
      this.status = 'RUNNING';
      this.sendIpcCommand({ command: 'resume' });
      eventBus.emit('agent.resumed', { runId: this.activeRunId }, this.activeProjectId, this.activeRunId);
      return true;
    }
    return false;
  }

  stopAgent() {
    if (this.currentAgentProcess) {
      this.status = 'STOPPED';
      this.sendIpcCommand({ command: 'stop' });

      setTimeout(() => {
        if (this.currentAgentProcess) {
          try {
            this.currentAgentProcess.kill('SIGKILL');
          } catch {}
          this.currentAgentProcess = null;
        }
      }, 3000);

      eventBus.emit('agent.stopped', { runId: this.activeRunId }, this.activeProjectId, this.activeRunId);
      return true;
    }
    return false;
  }

  overrideAgent(prompt) {
    if (this.currentAgentProcess) {
      this.sendIpcCommand({ command: 'override', prompt });
      eventBus.emit('agent.override', { prompt, runId: this.activeRunId }, this.activeProjectId, this.activeRunId);
      return true;
    }
    return false;
  }

  sendApprovalResponse(approvalId, decision) {
    const approval = db.prepare('SELECT * FROM approvals WHERE id = ?').get(approvalId);
    if (!approval) return false;

    const now = new Date().toISOString();
    const status = decision === 'REJECT' ? 'REJECTED' : 'APPROVED';
    db.prepare('UPDATE approvals SET status = ?, resolved_at = ? WHERE id = ?').run(status, now, approvalId);

    this.sendIpcCommand({
      command: 'approval_response',
      approvalId,
      decision,
      actionPayload: JSON.parse(approval.action_payload)
    });

    eventBus.emit(decision === 'REJECT' ? 'approval.rejected' : 'approval.granted', {
      approvalId,
      decision
    }, approval.project_id, approval.run_id);

    return true;
  }

  sendIpcCommand(payload) {
    if (this.currentAgentProcess && this.currentAgentProcess.stdin.writable) {
      this.currentAgentProcess.stdin.write(`IPC:CMD:${JSON.stringify(payload)}\n`);
    }
  }
}

module.exports = new AgentBridge();
