const { Client } = require('pg');
const bcrypt = require('bcryptjs');

const client = new Client({
  connectionString: 'postgresql://postgres.zbgzrkdmvtofyikksptq:vpjMKADVyUCg8u%23@aws-0-ap-southeast-2.pooler.supabase.com:6543/postgres'
});

async function seed() {
  await client.connect();
  console.log('Connected to PostgreSQL');

  const demoAccounts = [
    {
      email: 'admin@cyclecare.app',
      password: 'AdminPassword123!',
      role: 'ADMIN',
      display_name: 'CycleCare Admin',
      usage_mode: 'BOTH'
    },
    {
      email: 'demo@cyclecare.com',
      password: 'password123',
      role: 'USER',
      display_name: 'Aastha Sharma (Girl)',
      usage_mode: 'TRACK_CYCLE'
    },
    {
      email: 'husband.demo@cyclecare.app',
      password: 'password123',
      role: 'USER',
      display_name: 'Rahul Sharma (Husband)',
      usage_mode: 'SUPPORT_PARTNER'
    }
  ];

  for (const acc of demoAccounts) {
    const salt = await bcrypt.genSalt(10);
    const hash = await bcrypt.hash(acc.password, salt);

    const check = await client.query('SELECT id FROM public.users WHERE email = $1', [acc.email]);
    let userId;
    if (check.rows.length > 0) {
      userId = check.rows[0].id;
      await client.query(
        "UPDATE public.users SET password_hash = $1, role = $2, status = 'ACTIVE', usage_mode = $3, updated_at = NOW() WHERE id = $4",
        [hash, acc.role, acc.usage_mode, userId]
      );
      console.log('Updated user:', acc.email, userId);
    } else {
      const ins = await client.query(
        "INSERT INTO public.users (email, password_hash, role, status, usage_mode) VALUES ($1, $2, $3, 'ACTIVE', $4) RETURNING id",
        [acc.email, hash, acc.role, acc.usage_mode]
      );
      userId = ins.rows[0].id;
      console.log('Created user:', acc.email, userId);
    }

    const checkP = await client.query('SELECT id FROM public.profiles WHERE user_id = $1', [userId]);
    if (checkP.rows.length > 0) {
      await client.query('UPDATE public.profiles SET display_name = $1 WHERE user_id = $2', [acc.display_name, userId]);
    } else {
      await client.query('INSERT INTO public.profiles (user_id, display_name) VALUES ($1, $2)', [userId, acc.display_name]);
    }
  }

  // Connect Girl and Husband in partner_connections
  const userGirl = (await client.query("SELECT id FROM public.users WHERE email = 'demo@cyclecare.com'")).rows[0];
  const userHusband = (await client.query("SELECT id FROM public.users WHERE email = 'husband.demo@cyclecare.app'")).rows[0];

  if (userGirl && userHusband) {
    const checkConn = await client.query(
      'SELECT id FROM public.partner_connections WHERE requester_id = $1 AND recipient_id = $2',
      [userGirl.id, userHusband.id]
    );
    if (checkConn.rows.length === 0) {
      await client.query(
        "INSERT INTO public.partner_connections (requester_id, recipient_id, relationship, status) VALUES ($1, $2, 'Husband', 'ACCEPTED')",
        [userGirl.id, userHusband.id]
      );
      console.log('Created partner connection Girl <-> Husband');
    }
  }

  const allUsers = await client.query('SELECT u.id, u.email, u.role, u.usage_mode, p.display_name FROM public.users u LEFT JOIN public.profiles p ON u.id = p.user_id');
  console.log('Database users result:');
  console.table(allUsers.rows);

  await client.end();
}

seed().catch(err => {
  console.error('Seed error:', err);
  process.exit(1);
});
