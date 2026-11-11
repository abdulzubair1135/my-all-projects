const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const projectService = require('./projectService');
const eventBus = require('./eventBus');

const IGNORED_NAMES = new Set(['.git', 'node_modules', '.venv', 'venv', 'dist', 'build', '.coverage', '__pycache__']);

function calculateHash(content) {
  return crypto.createHash('sha256').update(content, 'utf8').digest('hex');
}

class FileService {
  /**
   * Resolves and validates that a relative path stays within the project root.
   */
  resolveSafePath(projectPath, relativePath = '') {
    if (!relativePath) return projectPath;

    // Prevent UNC and Windows device paths
    if (/^(\\\\|\/\/)|\b(CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])\b/i.test(relativePath)) {
      throw new Error('Invalid path: reserved Windows device or UNC path detected');
    }

    const fullPath = path.resolve(projectPath, relativePath);
    const canonicalProject = fs.realpathSync(projectPath);

    // Check if canonical target is strictly within canonical project
    let checkPath = fullPath;
    while (!fs.existsSync(checkPath) && checkPath !== path.dirname(checkPath)) {
      checkPath = path.dirname(checkPath);
    }

    const canonicalTarget = fs.existsSync(checkPath) ? fs.realpathSync(checkPath) : checkPath;

    const isWindows = process.platform === 'win32';
    const targetToCompare = isWindows ? canonicalTarget.toLowerCase() : canonicalTarget;
    const projectToCompare = isWindows ? canonicalProject.toLowerCase() : canonicalProject;

    if (!targetToCompare.startsWith(projectToCompare)) {
      throw new Error('Path traversal detected: Target path is outside workspace');
    }

    return fullPath;
  }

  getTree(projectId) {
    const project = projectService.getProject(projectId);
    if (!project) throw new Error('Project not found');

    const buildTree = (dirPath, relPath = '') => {
      const items = fs.readdirSync(dirPath, { withFileTypes: true });
      const tree = [];

      for (const item of items) {
        if (IGNORED_NAMES.has(item.name)) continue;

        const itemRelPath = path.join(relPath, item.name).replace(/\\/g, '/');
        const itemFullPath = path.join(dirPath, item.name);

        if (item.isDirectory()) {
          tree.push({
            name: item.name,
            path: itemRelPath,
            type: 'directory',
            children: buildTree(itemFullPath, itemRelPath)
          });
        } else {
          const stats = fs.statSync(itemFullPath);
          tree.push({
            name: item.name,
            path: itemRelPath,
            type: 'file',
            size: stats.size,
            updated_at: stats.mtime.toISOString()
          });
        }
      }

      // Sort directories first, then alphabetically
      return tree.sort((a, b) => {
        if (a.type === b.type) return a.name.localeCompare(b.name);
        return a.type === 'directory' ? -1 : 1;
      });
    };

    return buildTree(project.path);
  }

  getContent(projectId, relativePath) {
    const project = projectService.getProject(projectId);
    if (!project) throw new Error('Project not found');

    const safePath = this.resolveSafePath(project.path, relativePath);
    if (!fs.existsSync(safePath)) {
      throw new Error(`File not found: ${relativePath}`);
    }

    const stat = fs.statSync(safePath);
    if (stat.isDirectory()) {
      throw new Error(`Path is a directory: ${relativePath}`);
    }

    const content = fs.readFileSync(safePath, 'utf8');
    const hash = calculateHash(content);

    return {
      path: relativePath,
      content,
      hash,
      size: stat.size,
      updated_at: stat.mtime.toISOString()
    };
  }

  saveFile(projectId, relativePath, content, expectedHash = null) {
    const project = projectService.getProject(projectId);
    if (!project) throw new Error('Project not found');

    const safePath = this.resolveSafePath(project.path, relativePath);
    const parentDir = path.dirname(safePath);

    if (!fs.existsSync(parentDir)) {
      fs.mkdirSync(parentDir, { recursive: true });
    }

    let isNew = !fs.existsSync(safePath);

    if (!isNew && expectedHash) {
      const currentContent = fs.readFileSync(safePath, 'utf8');
      const currentHash = calculateHash(currentContent);
      if (currentHash !== expectedHash) {
        throw new Error('Conflict detected: File has been modified by another process');
      }
    }

    // Atomic write using temp file
    const tempPath = `${safePath}.${crypto.randomBytes(6).toString('hex')}.tmp`;
    fs.writeFileSync(tempPath, content, 'utf8');
    fs.renameSync(tempPath, safePath);

    const newHash = calculateHash(content);
    const stat = fs.statSync(safePath);

    const fileEvent = {
      path: relativePath,
      hash: newHash,
      size: stat.size,
      updated_at: stat.mtime.toISOString()
    };

    eventBus.emit(isNew ? 'file.created' : 'file.modified', fileEvent, projectId);

    return fileEvent;
  }

  createDirectory(projectId, relativePath) {
    const project = projectService.getProject(projectId);
    if (!project) throw new Error('Project not found');

    const safePath = this.resolveSafePath(project.path, relativePath);
    if (!fs.existsSync(safePath)) {
      fs.mkdirSync(safePath, { recursive: true });
      eventBus.emit('file.created', { path: relativePath, type: 'directory' }, projectId);
    }
    return { path: relativePath, success: true };
  }

  deleteFile(projectId, relativePath) {
    const project = projectService.getProject(projectId);
    if (!project) throw new Error('Project not found');

    const safePath = this.resolveSafePath(project.path, relativePath);
    if (!fs.existsSync(safePath)) {
      return { path: relativePath, deleted: false };
    }

    const stat = fs.statSync(safePath);
    if (stat.isDirectory()) {
      fs.rmSync(safePath, { recursive: true, force: true });
    } else {
      fs.unlinkSync(safePath);
    }

    eventBus.emit('file.deleted', { path: relativePath }, projectId);
    return { path: relativePath, deleted: true };
  }

  searchFiles(projectId, query) {
    const project = projectService.getProject(projectId);
    if (!project) throw new Error('Project not found');

    const results = [];
    const searchDir = (dirPath, relPath = '') => {
      const items = fs.readdirSync(dirPath, { withFileTypes: true });
      for (const item of items) {
        if (IGNORED_NAMES.has(item.name)) continue;
        const itemRel = path.join(relPath, item.name).replace(/\\/g, '/');
        const itemFull = path.join(dirPath, item.name);

        if (item.isDirectory()) {
          searchDir(itemFull, itemRel);
        } else {
          if (item.name.toLowerCase().includes(query.toLowerCase())) {
            results.push({ path: itemRel, type: 'filename_match' });
          } else {
            try {
              const content = fs.readFileSync(itemFull, 'utf8');
              if (content.includes(query)) {
                results.push({ path: itemRel, type: 'content_match' });
              }
            } catch {
              // Ignore binary read errors
            }
          }
        }
      }
    };

    searchDir(project.path);
    return results.slice(0, 50);
  }

  createProjectZip(projectId) {
    const project = projectService.getProject(projectId);
    if (!project) throw new Error('Project not found');
    if (!fs.existsSync(project.path)) throw new Error('Workspace folder does not exist');

    const safeName = (project.name || 'project').replace(/[^a-zA-Z0-9_-]/g, '_');
    const tempDir = path.resolve(__dirname, '../../../data');
    if (!fs.existsSync(tempDir)) fs.mkdirSync(tempDir, { recursive: true });
    const zipPath = path.join(tempDir, `${safeName}_${Date.now()}.zip`);

    const { execSync } = require('child_process');
    const pyScript = `import zipfile, os; p = r'''${project.path}'''; z = r'''${zipPath}'''; EX = {'node_modules', '.git', '.venv', 'venv', '__pycache__', 'dist', 'build'}; zipf = zipfile.ZipFile(z, 'w', zipfile.ZIP_DEFLATED); [zipf.write(os.path.join(root, f), os.path.relpath(os.path.join(root, f), p)) for root, dirs, files in os.walk(p) for f in files if f != '.agent_state.sqlite' and not any(ex in root.split(os.sep) for ex in EX)]; zipf.close()`;
    
    execSync(`python -c "${pyScript}"`);
    return { zipPath, fileName: `${safeName}.zip` };
  }
}

module.exports = new FileService();
