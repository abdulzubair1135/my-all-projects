const chokidar = require('chokidar');
const path = require('path');
const eventBus = require('./eventBus');

let currentWatcher = null;
let currentProjectId = null;

class FileWatcherService {
  watchProject(project) {
    if (currentWatcher) {
      currentWatcher.close();
      currentWatcher = null;
    }

    if (!project || !project.path) return;

    currentProjectId = project.id;
    currentWatcher = chokidar.watch(project.path, {
      ignored: [
        /(^|[\/\\])\../, // dot files
        /node_modules/,
        /\.venv/,
        /dist/,
        /build/,
        /\.tmp$/
      ],
      persistent: true,
      ignoreInitial: true,
      awaitWriteFinish: {
        stabilityThreshold: 300,
        pollInterval: 100
      }
    });

    currentWatcher
      .on('add', (filePath) => {
        const relPath = path.relative(project.path, filePath).replace(/\\/g, '/');
        eventBus.emit('file.created', { path: relPath, type: 'file' }, project.id);
      })
      .on('change', (filePath) => {
        const relPath = path.relative(project.path, filePath).replace(/\\/g, '/');
        eventBus.emit('file.modified', { path: relPath }, project.id);
      })
      .on('unlink', (filePath) => {
        const relPath = path.relative(project.path, filePath).replace(/\\/g, '/');
        eventBus.emit('file.deleted', { path: relPath }, project.id);
      })
      .on('error', (err) => {
        console.error('File watcher error:', err);
      });
  }

  stop() {
    if (currentWatcher) {
      currentWatcher.close();
      currentWatcher = null;
      currentProjectId = null;
    }
  }
}

module.exports = new FileWatcherService();
