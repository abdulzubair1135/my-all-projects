const fs = require('fs');
const path = require('path');
const config = require('../config/config');
const logger = require('../utils/logger');

let dbInstance = null;

/**
 * Initializes and returns the persistent SQLite database instance.
 * Uses Node's high-performance native SQLite engine with WAL mode.
 */
function getDatabase() {
  if (dbInstance) {
    return dbInstance;
  }

  try {
    let DatabaseEngine;
    try {
      // First attempt native node:sqlite (zero native compilation friction, built into Node)
      const { DatabaseSync } = require('node:sqlite');
      DatabaseEngine = DatabaseSync;
    } catch {
      // Fallback to better-sqlite3 if node:sqlite is unavailable
      DatabaseEngine = require('better-sqlite3');
    }

    dbInstance = new DatabaseEngine(config.databasePath);

    // Apply high-performance Pragmas
    dbInstance.exec('PRAGMA journal_mode = WAL;');
    dbInstance.exec('PRAGMA synchronous = NORMAL;');
    dbInstance.exec('PRAGMA foreign_keys = ON;');
    dbInstance.exec('PRAGMA temp_store = MEMORY;');

    logger.info('DATABASE', `SQLite initialized in WAL mode at ${config.databasePath}`);

    // Load and execute schema
    const schemaPath = path.join(__dirname, 'schema.sql');
    const schemaSql = fs.readFileSync(schemaPath, 'utf8');
    dbInstance.exec(schemaSql);

    logger.info('DATABASE', 'Database schema applied successfully');
    return dbInstance;
  } catch (error) {
    logger.error('DATABASE', `Database initialization error: ${error.message}`, { error: error.stack });
    throw error;
  }
}

/**
 * Executes a function inside an immediate SQLite transaction.
 * @param {Function} fn 
 */
function transaction(fn) {
  const db = getDatabase();
  db.exec('BEGIN IMMEDIATE TRANSACTION;');
  try {
    const result = fn(db);
    db.exec('COMMIT;');
    return result;
  } catch (error) {
    db.exec('ROLLBACK;');
    throw error;
  }
}

/**
 * Closes the database connection cleanly.
 */
function closeDatabase() {
  if (dbInstance) {
    try {
      dbInstance.close();
      logger.info('DATABASE', 'Database connection closed');
    } catch (err) {
      logger.error('DATABASE', `Error closing database: ${err.message}`);
    }
    dbInstance = null;
  }
}

module.exports = {
  getDatabase,
  transaction,
  closeDatabase
};
