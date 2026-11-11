import mysql from 'mysql2/promise';
import fs from 'fs';
import { env } from './src/config/env.js';

async function checkDatabase() {
  console.log('Connecting to Live Aiven MySQL...');
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
    // 1. Show Tables
    const [tables] = await connection.query('SHOW TABLES');
    console.log('\n=== Database Tables ===');
    console.table(tables.map(t => Object.values(t)[0]));

    // 2. Show Listings Count
    const [[{ count: listingsCount }]] = await connection.query('SELECT COUNT(*) as count FROM listings');
    console.log(`\nTotal Listings in DB: ${listingsCount}`);

    // 3. Show Bookings Count
    const [[{ count: bookingsCount }]] = await connection.query('SELECT COUNT(*) as count FROM bookings');
    console.log(`Total Bookings in DB: ${bookingsCount}`);

    if (bookingsCount > 0) {
      const [bookings] = await connection.query('SELECT id, listing_id, start_date, end_date, total_amount FROM bookings LIMIT 5');
      console.log('\n=== Recent Bookings (First 5) ===');
      console.table(bookings);
    } else {
      console.log('\n(Aapne abhi tak koi booking nahi ki hai. App kholkar ek booking karein, fir ye script dubara chalayein!)');
    }

  } catch (err) {
    console.error('Error querying database:', err.message);
  } finally {
    await connection.end();
  }
}

checkDatabase();
