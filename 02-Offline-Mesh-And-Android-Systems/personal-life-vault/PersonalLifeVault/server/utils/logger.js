const fs = require('fs');
const path = require('path');
const config = require('../config/config');

const logFilePath = path.join(config.logDirectory, 'vault.log');

function writeLog(level, category, message, meta = {}) {
  const timestamp = new Date().toISOString();
  // Sanitize meta to never log tokens, passwords, or secret keys
  const safeMeta = { ...meta };
  delete safeMeta.token;
  delete safeMeta.auth_token;
  delete safeMeta.admin_key;
  delete safeMeta.password;
  delete safeMeta.secret;

  const logEntry = {
    timestamp,
    level,
    category,
    message,
    ...(Object.keys(safeMeta).length > 0 ? { meta: safeMeta } : {})
  };

  const line = JSON.stringify(logEntry) + '\n';

  // Console output
  const prefix = `[${timestamp}] [${level.toUpperCase()}] [${category}]`;
  if (level === 'error') {
    console.error(`${prefix} ${message}`, Object.keys(safeMeta).length ? safeMeta : '');
  } else if (level === 'warn') {
    console.warn(`${prefix} ${message}`, Object.keys(safeMeta).length ? safeMeta : '');
  } else {
    console.log(`${prefix} ${message}`, Object.keys(safeMeta).length ? safeMeta : '');
  }

  // Persistent file append
  fs.appendFile(logFilePath, line, (err) => {
    if (err) {
      console.error('Failed writing to log file:', err.message);
    }
  });
}

module.exports = {
  info: (category, message, meta) => writeLog('info', category, message, meta),
  warn: (category, message, meta) => writeLog('warn', category, message, meta),
  error: (category, message, meta) => writeLog('error', category, message, meta),
  logFilePath
};
