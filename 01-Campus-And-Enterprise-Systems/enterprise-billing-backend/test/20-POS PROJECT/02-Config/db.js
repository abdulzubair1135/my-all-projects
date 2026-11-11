/**
 * POS Application MySQL Connection Pool (mysql2/promise)
 */

import mysql from 'mysql2/promise';
import dotenv from 'dotenv';

dotenv.config();

const pool = mysql.createPool({
  host: process.env.DB_HOST || 'localhost',
  user: process.env.DB_USER || 'root',
  password: process.env.DB_PASSWORD || '',
  database: process.env.DB_NAME || 'pos_db',
  port: Number(process.env.DB_PORT) || 3306,
  waitForConnections: true,
  connectionLimit: 10,
  queueLimit: 0
});

export const testConnection = async () => {
  try {
    const conn = await pool.getConnection();
    console.log('✅ POS MySQL Database Connected');
    conn.release();
  } catch (error) {
    console.error('❌ POS Database Connection Failed:', error.message);
  }
};

export default pool;
