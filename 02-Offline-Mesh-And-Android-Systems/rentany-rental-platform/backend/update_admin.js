import mysql from 'mysql2/promise';
import bcrypt from 'bcryptjs';
import fs from 'fs';
import { env } from './src/config/env.js';

async function updateAdmin() {
  console.log('Connecting to Live Aiven MySQL to update admin credentials...');
  const connection = await mysql.createConnection({
    host: env.DB_HOST,
    port: env.DB_PORT,
    user: env.DB_USER,
    password: env.DB_PASSWORD,
    database: env.DB_NAME,
    ssl: {
      ca: fs.readFileSync(env.DB_SSL_CA, 'utf8'),
      rejectUnauthorized: true
    }
  });

  try {
    const passwordHash = await bcrypt.hash('danish123', 10);
    const [res] = await connection.query(
      "UPDATE users SET email = 'admin123@gmail.com', password_hash = ? WHERE role = 'admin'",
      [passwordHash]
    );

    if (res.affectedRows > 0) {
      console.log('SUCCESS: Admin credentials updated in the database!');
      console.log('Email: admin123@gmail.com');
      console.log('Password: danish123');
    } else {
      console.log('WARN: No user with role "admin" was found to update.');
    }
  } catch (err) {
    console.error('Failed to update admin credentials:', err.message);
  } finally {
    await connection.end();
  }
}

updateAdmin();
