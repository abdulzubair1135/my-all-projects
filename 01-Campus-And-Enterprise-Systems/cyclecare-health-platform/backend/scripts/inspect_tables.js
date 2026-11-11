const pool = require('../src/config/db');

async function main() {
  const t1 = await pool.query("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'partner_connections'");
  console.log('partner_connections columns:', t1.rows);

  const t2 = await pool.query("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'partner_permissions'");
  console.log('partner_permissions columns:', t2.rows);

  const t3 = await pool.query("SELECT conname, pg_get_constraintdef(c.oid) FROM pg_constraint c JOIN pg_namespace n ON n.oid = c.connamespace WHERE conrelid = 'partner_connections'::regclass");
  console.log('partner_connections constraints:', t3.rows);

  const t4 = await pool.query("SELECT conname, pg_get_constraintdef(c.oid) FROM pg_constraint c JOIN pg_namespace n ON n.oid = c.connamespace WHERE conrelid = 'partner_permissions'::regclass");
  console.log('partner_permissions constraints:', t4.rows);

  process.exit(0);
}

main().catch(err => {
  console.error(err);
  process.exit(1);
});
