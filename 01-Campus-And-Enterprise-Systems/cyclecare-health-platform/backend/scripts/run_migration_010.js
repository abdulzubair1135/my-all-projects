const pool = require('../src/config/db');
const fs = require('fs');
const path = require('path');

async function run() {
  const sqlPath = path.join(__dirname, '../../database/migrations/010_relationship_aware_partner_and_family_sharing.sql');
  const sql = fs.readFileSync(sqlPath, 'utf8');
  console.log('Running Migration 010...');
  await pool.query(sql);
  console.log('Migration 010 applied successfully!');
  process.exit(0);
}

run().catch(err => {
  console.error('Migration error:', err);
  process.exit(1);
});
