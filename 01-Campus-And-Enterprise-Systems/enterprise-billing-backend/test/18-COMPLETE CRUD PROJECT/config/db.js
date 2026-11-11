/**
 * Database Connection Setup using mysql2/promise
 * Direct promises support karta hai async/await syntax ke sath.
 */

import mysql from 'mysql2/promise';
import dotenv from 'dotenv';

dotenv.config();

// MySQL Connection Pool create kar rahe hain for efficiency
const pool = mysql.createPool({
  host: process.env.DB_HOST || 'localhost',
  user: process.env.DB_USER || 'root',
  password: process.env.DB_PASSWORD || '',
  database: process.env.DB_NAME || 'crud_db',
  port: Number(process.env.DB_PORT) || 3306,
  waitForConnections: true,
  connectionLimit: 10,
  queueLimit: 0
});

// Quick Connection Test
export const testConnection = async () => {
  try {
    const connection = await pool.getConnection();
    console.log('✅ Database connected successfully to MySQL');
    connection.release();
  } catch (error) {
    console.error('❌ Database connection failed:', error.message);
  }
};

export default pool;
