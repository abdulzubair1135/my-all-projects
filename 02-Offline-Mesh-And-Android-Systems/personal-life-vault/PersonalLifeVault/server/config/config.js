const path = require('path');
const fs = require('fs');
require('dotenv').config();

const storageRoot = path.resolve(process.env.VAULT_STORAGE_ROOT || 'C:\\Vault');
const databasePath = process.env.DATABASE_FILE 
  ? path.resolve(process.env.DATABASE_FILE) 
  : path.join(storageRoot, 'vault.db');

// Ensure root storage directory exists
if (!fs.existsSync(storageRoot)) {
  fs.mkdirSync(storageRoot, { recursive: true });
}

// Ensure database directory exists if separate
const dbDir = path.dirname(databasePath);
if (!fs.existsSync(dbDir)) {
  fs.mkdirSync(dbDir, { recursive: true });
}

// Ensure logs directory exists
const logDirectory = path.join(__dirname, '..', 'logs');
if (!fs.existsSync(logDirectory)) {
  fs.mkdirSync(logDirectory, { recursive: true });
}

module.exports = {
  port: parseInt(process.env.PORT || '8088', 10),
  host: process.env.HOST || '0.0.0.0',
  env: process.env.NODE_ENV || 'development',
  storageRoot,
  databasePath,
  timezone: process.env.VAULT_TIMEZONE || 'Asia/Kolkata',
  adminRegistrationKey: process.env.ADMIN_REGISTRATION_KEY || 'ChangeThisMasterKeyBeforeProductionSync123!',
  logDirectory
};
