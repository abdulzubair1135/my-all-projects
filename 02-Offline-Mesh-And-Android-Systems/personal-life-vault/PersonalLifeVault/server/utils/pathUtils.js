const path = require('path');
const fs = require('fs');
const config = require('../config/config');

/**
 * Validates that targetPath is strictly inside rootPath, preventing directory traversal.
 * @param {string} targetPath 
 * @param {string} rootPath 
 * @returns {boolean}
 */
function isPathInsideRoot(targetPath, rootPath = config.storageRoot) {
  const relative = path.relative(path.resolve(rootPath), path.resolve(targetPath));
  return !relative.startsWith('..') && !path.isAbsolute(relative);
}

/**
 * Sanitizes a filename to prevent directory traversal and illegal Windows/Linux characters.
 * @param {string} fileName 
 * @returns {string}
 */
function sanitizeFileName(fileName) {
  if (!fileName || typeof fileName !== 'string') {
    return 'unnamed_file';
  }
  // Strip paths
  const base = path.basename(fileName);
  // Remove control characters and illegal filesystem chars: / ? < > \ : * | " ^
  let clean = base.replace(/[<>:"/\\|?*\x00-\x1F]/g, '_').trim();
  if (clean.length === 0 || clean === '.' || clean === '..') {
    clean = 'vault_file';
  }
  // Limit length
  if (clean.length > 200) {
    const ext = path.extname(clean);
    const stem = path.basename(clean, ext).substring(0, 190);
    clean = stem + ext;
  }
  return clean;
}

/**
 * Returns formatted date components based on UTC or target timezone timestamp.
 * Format: { year: '2026', month: '09', dayString: '2026-09-28' }
 * @param {number} timestampMs 
 * @param {string} timezone 
 */
function getDateComponents(timestampMs, timezone = config.timezone) {
  const date = new Date(timestampMs || Date.now());
  const formatter = new Intl.DateTimeFormat('en-CA', {
    timeZone: timezone,
    year: 'numeric',
    month: '2-digit',
    day: '2-digit'
  });
  
  // Format returns 'YYYY-MM-DD'
  const parts = formatter.formatToParts(date);
  const year = parts.find(p => p.type === 'year')?.value || '1970';
  const month = parts.find(p => p.type === 'month')?.value || '01';
  const day = parts.find(p => p.type === 'day')?.value || '01';
  const dayString = `${year}-${month}-${day}`;

  return { year, month, dayString };
}

/**
 * Ensures and returns the date-structured media directory.
 * E.g., C:\Vault\2026\09\2026-09-28\media
 * @param {number} timestampMs 
 * @param {string} subFolder 'media' | 'metadata' | 'exports'
 * @returns {string} Absolute directory path
 */
function ensureDateDirectory(timestampMs, subFolder = 'media') {
  const { year, month, dayString } = getDateComponents(timestampMs);
  const dirPath = path.join(config.storageRoot, year, month, dayString, subFolder);

  if (!isPathInsideRoot(dirPath, config.storageRoot)) {
    throw new Error('Path traversal attempt detected');
  }

  if (!fs.existsSync(dirPath)) {
    fs.mkdirSync(dirPath, { recursive: true });
  }

  return dirPath;
}

/**
 * Generates a collision-free target file path in destination directory.
 * E.g., recording.m4a -> recording_1.m4a -> recording_2.m4a
 * @param {string} directory 
 * @param {string} originalName 
 * @returns {string} Safe absolute file path that doesn't yet exist
 */
function getUniqueFilePath(directory, originalName) {
  const safeName = sanitizeFileName(originalName);
  const ext = path.extname(safeName);
  const stem = path.basename(safeName, ext);

  let targetPath = path.join(directory, safeName);
  let counter = 1;

  while (fs.existsSync(targetPath)) {
    targetPath = path.join(directory, `${stem}_${counter}${ext}`);
    counter++;
  }

  if (!isPathInsideRoot(targetPath, config.storageRoot)) {
    throw new Error('Path traversal attempt detected in target file path');
  }

  return targetPath;
}

module.exports = {
  isPathInsideRoot,
  sanitizeFileName,
  getDateComponents,
  ensureDateDirectory,
  getUniqueFilePath
};
