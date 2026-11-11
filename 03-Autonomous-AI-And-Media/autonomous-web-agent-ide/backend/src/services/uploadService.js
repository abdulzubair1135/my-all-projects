/**
 * uploadService.js
 * Handles image uploads and ZIP import/extraction for Autonomous Web-Agent IDE.
 */

const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const unzipper = require('unzipper');
const archiver = require('archiver');
const { execSync } = require('child_process');
const projectService = require('./projectService');

const WORKSPACE_ROOT = path.resolve(
  process.env.WORKSPACE_ROOT || path.join(__dirname, '../../..', 'workspace')
);

/**
 * Ensure upload directory exists for a project.
 */
function getUploadDir(projectId) {
  const project = projectService.getProject(projectId);
  if (!project) throw new Error(`Project not found: ${projectId}`);
  const uploadDir = path.join(project.path, '.uploads');
  fs.mkdirSync(uploadDir, { recursive: true });
  return uploadDir;
}

/**
 * Save an uploaded image file to the project's .uploads/ directory.
 * Returns the saved file path (relative to project root).
 */
function saveImage(projectId, originalName, buffer) {
  const uploadDir = getUploadDir(projectId);
  const ext = path.extname(originalName) || '.png';
  const timestamp = Date.now();
  const hash = crypto.createHash('md5').update(buffer).digest('hex').slice(0, 8);
  const fileName = `img_${timestamp}_${hash}${ext}`;
  const fullPath = path.join(uploadDir, fileName);

  fs.writeFileSync(fullPath, buffer);

  return {
    fileName,
    fullPath,
    relativePath: path.join('.uploads', fileName),
    sizeBytes: buffer.length,
    mimeType: getMimeType(ext),
  };
}

/**
 * Extract a ZIP archive into the project workspace.
 * Creates a git checkpoint before extraction if git is available.
 * Returns a summary of extracted files.
 */
async function extractZip(projectId, zipBuffer) {
  const project = projectService.getProject(projectId);
  if (!project) throw new Error(`Project not found: ${projectId}`);

  const workspacePath = project.path;

  // Create a git checkpoint before extraction
  let checkpointCreated = false;
  try {
    execSync('git rev-parse --is-inside-work-tree', { cwd: workspacePath, stdio: 'ignore' });
    execSync('git add -A', { cwd: workspacePath, stdio: 'ignore' });
    execSync(`git commit -m "checkpoint: before ZIP import ${new Date().toISOString()}" --allow-empty`, {
      cwd: workspacePath,
      stdio: 'ignore',
    });
    checkpointCreated = true;
  } catch {
    // Git not initialized or no changes — safe to continue
  }

  // Write zip to temp file
  const tmpZip = path.join(workspacePath, '.tmp_import.zip');
  fs.writeFileSync(tmpZip, zipBuffer);

  const extractedFiles = [];
  const skippedFiles = [];

  // Security: deny paths with traversal or absolute paths
  const DENY_PATTERNS = [
    /^\//,          // absolute unix path
    /^[A-Z]:\\/i,  // absolute windows path
    /\.\.\//,       // directory traversal
    /\.\.\\/, 
    /node_modules/, // skip node_modules
    /\.git\//,      // skip .git
    /\.git\\/,
  ];

  try {
    const directory = await unzipper.Open.buffer(zipBuffer);
    
    for (const entry of directory.files) {
      const entryPath = entry.path;

      // Security check
      const isDenied = DENY_PATTERNS.some((p) => p.test(entryPath));
      if (isDenied) {
        skippedFiles.push({ path: entryPath, reason: 'security' });
        continue;
      }

      const destPath = path.join(workspacePath, entryPath);

      if (entry.type === 'Directory') {
        fs.mkdirSync(destPath, { recursive: true });
      } else {
        // Ensure parent directory exists
        fs.mkdirSync(path.dirname(destPath), { recursive: true });
        const content = await entry.buffer();
        fs.writeFileSync(destPath, content);
        extractedFiles.push(entryPath);
      }
    }
  } finally {
    // Clean up temp zip
    try { fs.unlinkSync(tmpZip); } catch {}
  }

  return {
    extractedFiles,
    skippedFiles,
    totalExtracted: extractedFiles.length,
    checkpointCreated,
    workspacePath,
  };
}

/**
 * List all uploaded images for a project.
 */
function listUploads(projectId) {
  const project = projectService.getProject(projectId);
  if (!project) return [];

  const uploadDir = path.join(project.path, '.uploads');
  if (!fs.existsSync(uploadDir)) return [];

  return fs.readdirSync(uploadDir)
    .filter((f) => /\.(png|jpg|jpeg|webp|gif|bmp|svg)$/i.test(f))
    .map((f) => {
      const fullPath = path.join(uploadDir, f);
      const stat = fs.statSync(fullPath);
      return {
        fileName: f,
        fullPath,
        relativePath: path.join('.uploads', f),
        sizeBytes: stat.size,
        createdAt: stat.birthtime.toISOString(),
      };
    })
    .sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt));
}

/**
 * Delete an uploaded image.
 */
function deleteUpload(projectId, fileName) {
  const project = projectService.getProject(projectId);
  if (!project) throw new Error('Project not found');

  // Security: only allow simple filenames, no path traversal
  if (fileName.includes('/') || fileName.includes('\\') || fileName.includes('..')) {
    throw new Error('Invalid filename');
  }

  const filePath = path.join(project.path, '.uploads', fileName);
  if (!fs.existsSync(filePath)) throw new Error('File not found');
  fs.unlinkSync(filePath);
  return { success: true };
}

/**
 * Create a ZIP of the entire project (for Export ZIP).
 * Returns a stream.
 */
function createProjectZipStream(projectId, outputPath) {
  const project = projectService.getProject(projectId);
  if (!project) throw new Error('Project not found');

  return new Promise((resolve, reject) => {
    const output = fs.createWriteStream(outputPath);
    const archive = archiver('zip', { zlib: { level: 9 } });

    output.on('close', () => resolve({ size: archive.pointer() }));
    archive.on('error', reject);

    archive.pipe(output);
    archive.glob('**/*', {
      cwd: project.path,
      ignore: [
        'node_modules/**',
        '.git/**',
        '.uploads/**',
        'dist/**',
        'build/**',
        '.tmp_import.zip',
      ],
    });
    archive.finalize();
  });
}

function getMimeType(ext) {
  const map = {
    '.png': 'image/png',
    '.jpg': 'image/jpeg',
    '.jpeg': 'image/jpeg',
    '.webp': 'image/webp',
    '.gif': 'image/gif',
    '.bmp': 'image/bmp',
    '.svg': 'image/svg+xml',
  };
  return map[ext.toLowerCase()] || 'application/octet-stream';
}

module.exports = {
  saveImage,
  extractZip,
  listUploads,
  deleteUpload,
  createProjectZipStream,
};
