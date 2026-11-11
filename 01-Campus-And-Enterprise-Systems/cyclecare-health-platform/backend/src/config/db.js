const { Pool } = require('pg');
const dns = require('dns');
require('dotenv').config();

// Use reliable Google & Cloudflare DNS to prevent local ISP ESERVFAIL drops
try {
  dns.setServers(['8.8.8.8', '1.1.1.1']);
} catch (_) {}

const connectionString = process.env.DATABASE_URL || 
  'postgresql://postgres.zbgzrkdmvtofyikksptq:vpjMKADVyUCg8u%23@aws-0-ap-southeast-2.pooler.supabase.com:6543/postgres';

const pool = new Pool({
  connectionString,
  max: 15,
  idleTimeoutMillis: 2000,
  connectionTimeoutMillis: 15000,
  keepAlive: true,
  keepAliveInitialDelayMillis: 10000
});

pool.on('error', (err) => {
  console.error('Unexpected error on idle PostgreSQL client', err);
});

module.exports = pool;
