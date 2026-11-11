const { v4: uuidv4 } = require('uuid');
const path = require('path');
const fs = require('fs');
const { db } = require('../database/db');
const eventBus = require('./eventBus');

const WORKSPACE_ROOT = process.env.WORKSPACE_ROOT 
  ? path.resolve(process.env.WORKSPACE_ROOT) 
  : path.resolve(__dirname, '../../../workspace');

// Ensure workspace root directory exists
if (!fs.existsSync(WORKSPACE_ROOT)) {
  fs.mkdirSync(WORKSPACE_ROOT, { recursive: true });
}

class ProjectService {
  createProject(name, prompt = '') {
    const id = uuidv4();
    const sanitizedName = name.replace(/[^a-zA-Z0-9_-]/g, '_').toLowerCase() || 'project';
    let projectFolder = sanitizedName;
    let projectPath = path.join(WORKSPACE_ROOT, projectFolder);
    if (fs.existsSync(projectPath)) {
      projectFolder = `${sanitizedName}_${id.substring(0, 6)}`;
      projectPath = path.join(WORKSPACE_ROOT, projectFolder);
    }

    if (!fs.existsSync(projectPath)) {
      fs.mkdirSync(projectPath, { recursive: true });
    }

    const now = new Date().toISOString();
    const stmt = db.prepare(`
      INSERT INTO projects (id, name, path, prompt, status, created_at, updated_at)
      VALUES (?, ?, ?, ?, 'PENDING', ?, ?)
    `);
    stmt.run(id, name, projectPath, prompt, now, now);

    const project = this.getProject(id);
    eventBus.emit('project.created', project, id);
    return project;
  }

  getProject(id) {
    if (!id) return null;
    let stmt = db.prepare('SELECT * FROM projects WHERE id = ?');
    let project = stmt.get(id);
    if (project) return project;

    // Fallback 1: match by name
    stmt = db.prepare('SELECT * FROM projects WHERE name = ? OR LOWER(name) = LOWER(?)');
    project = stmt.get(id, id);
    if (project) return project;

    // Fallback 2: match by path
    stmt = db.prepare('SELECT * FROM projects WHERE path = ?');
    project = stmt.get(id);
    if (project) return project;

    // Fallback 3: auto-register workspace folder if it exists physically
    const potentialFolder = path.join(WORKSPACE_ROOT, id);
    if (fs.existsSync(potentialFolder)) {
      const now = new Date().toISOString();
      const newId = uuidv4();
      db.prepare(`
        INSERT INTO projects (id, name, path, prompt, status, created_at, updated_at)
        VALUES (?, ?, ?, '', 'COMPLETED', ?, ?)
      `).run(newId, id, potentialFolder, now, now);
      return this.getProject(newId);
    }

    return null;
  }

  listProjects() {
    // Auto-discover any projects physically located in workspace root
    try {
      if (fs.existsSync(WORKSPACE_ROOT)) {
        const entries = fs.readdirSync(WORKSPACE_ROOT, { withFileTypes: true });
        const now = new Date().toISOString();
        for (const entry of entries) {
          if (entry.isDirectory() && !entry.name.startsWith('.')) {
            const folderPath = path.join(WORKSPACE_ROOT, entry.name);
            const existing = db.prepare('SELECT id FROM projects WHERE path = ? OR name = ?').get(folderPath, entry.name);
            if (!existing) {
              const id = uuidv4();
              db.prepare(`
                INSERT INTO projects (id, name, path, prompt, status, created_at, updated_at)
                VALUES (?, ?, ?, '', 'COMPLETED', ?, ?)
              `).run(id, entry.name, folderPath, now, now);
            }
          }
        }
      }
    } catch {}

    const stmt = db.prepare('SELECT * FROM projects ORDER BY updated_at DESC, created_at DESC');
    return stmt.all();
  }

  updateProjectStatus(id, status) {
    const now = new Date().toISOString();
    const stmt = db.prepare('UPDATE projects SET status = ?, updated_at = ? WHERE id = ?');
    stmt.run(status, now, id);
    eventBus.emit('project.updated', { id, status }, id);
  }

  deleteProject(id) {
    const project = this.getProject(id);
    if (!project) return false;

    // Delete folder if exists
    if (fs.existsSync(project.path)) {
      try {
        fs.rmSync(project.path, { recursive: true, force: true });
      } catch (err) {
        console.error(`Error deleting project folder ${project.path}:`, err);
      }
    }

    const stmt = db.prepare('DELETE FROM projects WHERE id = ?');
    stmt.run(id);
    eventBus.emit('project.deleted', { id }, id);
    return true;
  }
}

module.exports = new ProjectService();
