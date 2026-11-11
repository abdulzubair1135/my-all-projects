import mysql from 'mysql2/promise';
import dotenv from 'dotenv';

dotenv.config();

const pool = mysql.createPool({
  host: process.env.DB_HOST || 'localhost',
  user: process.env.DB_USER || 'root',
  password: process.env.DB_PASS || '',
  database: process.env.DB_NAME || 'master_store_db',
  waitForConnections: true,
  connectionLimit: 15,
  queueLimit: 0
});

// Test Connection
pool.getConnection()
  .then((conn) => {
    console.log('✅ MySQL Pool connected successfully to master_store_db');
    conn.release();
  })
  .catch((err) => {
    console.error('❌ Database Connection Error:', err.message);
  });

export default pool;
