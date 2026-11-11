import fs from 'fs';
import path from 'path';
import mysql from 'mysql2/promise';
import dotenv from 'dotenv';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Load environment variables
dotenv.config({ path: path.join(__dirname, '../../.env') });

const {
  DB_HOST = 'localhost',
  DB_PORT = 3306,
  DB_USER = 'root',
  DB_PASSWORD = '',
  DB_NAME = 'rentany'
} = process.env;

async function migrate() {
  console.log('Starting MySQL Migration...');
  
  // 1. First connect without specifying the database to ensure it exists
  let connection;
  try {
    const sslOptions = process.env.DB_SSL === 'true' ? { rejectUnauthorized: false } : null;
    connection = await mysql.createConnection({
      host: DB_HOST,
      port: Number(DB_PORT),
      user: DB_USER,
      password: DB_PASSWORD,
      multipleStatements: true, // Allow running multi-statements
      ssl: sslOptions
    });
    console.log('Connected to MySQL server successfully.');
  } catch (err) {
    console.error('Failed to connect to MySQL server:', err.message);
    process.exit(1);
  }

  try {
    // Create DB if not exists
    await connection.query(`CREATE DATABASE IF NOT EXISTS \`${DB_NAME}\` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;`);
    console.log(`Database "${DB_NAME}" created or verified.`);
    
    // Switch to database
    await connection.changeUser({ database: DB_NAME });
    console.log(`Using database: "${DB_NAME}"`);

    // Read schema.sql
    const schemaPath = path.join(__dirname, 'schema.sql');
    if (!fs.existsSync(schemaPath)) {
      throw new Error(`Schema file not found at ${schemaPath}`);
    }
    
    const schemaSql = fs.readFileSync(schemaPath, 'utf8');
    
    // Execute the schema queries
    // mysql2 supports multipleStatements, so we can execute the whole schema.sql in one go!
    console.log('Executing schema.sql queries...');
    await connection.query(schemaSql);
    console.log('Database tables, constraints, and indexes built successfully.');
    
  } catch (err) {
    console.error('Error executing migration:', err.message);
    process.exit(1);
  } finally {
    if (connection) {
      await connection.end();
      console.log('Migration connection closed.');
    }
  }
}

migrate();
