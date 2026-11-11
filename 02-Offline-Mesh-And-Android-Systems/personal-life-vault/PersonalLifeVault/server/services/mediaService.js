const fs = require('fs');
const path = require('path');
const { getDatabase } = require('../database/database');
const { computeFileHash } = require('./hashService');
const { ensureDateDirectory, getUniqueFilePath, isPathInsideRoot } = require('../utils/pathUtils');
const logger = require('../utils/logger');
const config = require('../config/config');

/**
 * Processes an incoming uploaded media file with SHA-256 deduplication and date partitioning.
 * 
 * @param {string} deviceId 
 * @param {object} tempFile Multer file object
 * @param {object} metadata { timestamp, mime_type, client_hash, client_event_id }
 */
async function processMediaUpload(deviceId, tempFile, metadata) {
  const tempPath = tempFile.path;
  const originalName = tempFile.originalname || 'unnamed_media';
  const timestamp = parseInt(metadata.timestamp, 10) || Date.now();
  const mimeType = metadata.mime_type || tempFile.mimetype || 'application/octet-stream';
  const clientHash = metadata.client_hash ? metadata.client_hash.toLowerCase().trim() : null;
  const clientEventId = metadata.client_event_id || null;
  const fileSize = tempFile.size;

  try {
    // 1. Calculate actual SHA-256 of uploaded file
    const calculatedHash = (await computeFileHash(tempPath)).toLowerCase();

    // 2. Validate client hash if supplied
    if (clientHash && clientHash !== calculatedHash) {
      if (fs.existsSync(tempPath)) {
        fs.unlinkSync(tempPath);
      }
      logger.warn('MEDIA', 'Hash mismatch detected', {
        deviceId,
        clientHash,
        calculatedHash,
        originalName
      });
      const error = new Error('Integrity check failed: Client hash does not match computed SHA-256');
      error.status = 400;
      throw error;
    }

    const db = getDatabase();

    // 3. Check for existing duplicate file by SHA-256 hash
    const existing = db.prepare('SELECT id, file_hash, local_path, original_name FROM media_files WHERE file_hash = ?').get(calculatedHash);

    if (existing) {
      // Physical deduplication: delete the duplicate temp upload
      if (fs.existsSync(tempPath)) {
        fs.unlinkSync(tempPath);
      }

      logger.info('MEDIA', `Deduplicated file with existing hash: ${calculatedHash}`, {
        deviceId,
        originalName,
        existingPath: existing.local_path
      });

      return {
        success: true,
        duplicate: true,
        file_hash: existing.file_hash,
        local_path: existing.local_path,
        message: 'File with identical SHA-256 already exists in Vault, deduplicated'
      };
    }

    // 4. Ensure target date directory: C:\Vault\YYYY\MM\YYYY-MM-DD\media\
    const targetDir = ensureDateDirectory(timestamp, 'media');
    const finalFilePath = getUniqueFilePath(targetDir, originalName);

    if (!isPathInsideRoot(finalFilePath, config.storageRoot)) {
      if (fs.existsSync(tempPath)) {
        fs.unlinkSync(tempPath);
      }
      throw new Error('Destination path traversal violation');
    }

    // 5. Move file from temp to final partitioned vault location
    fs.renameSync(tempPath, finalFilePath);

    // 6. Record metadata in SQLite
    const now = Date.now();
    db.prepare(`
      INSERT INTO media_files (
        client_event_id, device_id, original_name, file_hash, local_path, mime_type, file_size, timestamp, created_at
      ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    `).run(
      clientEventId,
      deviceId,
      originalName,
      calculatedHash,
      finalFilePath,
      mimeType,
      fileSize,
      timestamp,
      now
    );

    logger.info('MEDIA', `Successfully vaulted new media: ${originalName} (${fileSize} bytes)`, {
      deviceId,
      finalFilePath,
      hash: calculatedHash
    });

    return {
      success: true,
      duplicate: false,
      file_hash: calculatedHash,
      local_path: finalFilePath,
      file_size: fileSize,
      message: 'Media securely stored and indexed in Vault'
    };
  } catch (error) {
    if (fs.existsSync(tempPath)) {
      try {
        fs.unlinkSync(tempPath);
      } catch {
        // ignore cleanup error
      }
    }
    throw error;
  }
}

module.exports = {
  processMediaUpload
};
