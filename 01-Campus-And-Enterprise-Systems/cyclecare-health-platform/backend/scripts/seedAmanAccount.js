const { Client } = require('pg');
const bcrypt = require('bcryptjs');

const client = new Client({
  connectionString: 'postgresql://postgres.zbgzrkdmvtofyikksptq:vpjMKADVyUCg8u%23@aws-0-ap-southeast-2.pooler.supabase.com:6543/postgres'
});

async function setupAmanAndConnections() {
  await client.connect();
  console.log('Connected to DB');

  // 1. Create or update Aman Sharma (Husband)
  const salt = await bcrypt.genSalt(10);
  const hash = await bcrypt.hash('password123', salt);

  const checkAman = await client.query("SELECT id FROM users WHERE email = 'aman.husband@cyclecare.app'");
  let amanId;
  if (checkAman.rows.length > 0) {
    amanId = checkAman.rows[0].id;
    await client.query(
      "UPDATE users SET password_hash = $1, role = 'USER', status = 'ACTIVE', usage_mode = 'SUPPORT_PARTNER', cyclecare_id = 'aman_husband', updated_at = NOW() WHERE id = $2",
      [hash, amanId]
    );
  } else {
    const ins = await client.query(
      "INSERT INTO users (email, password_hash, role, status, usage_mode, cyclecare_id) VALUES ('aman.husband@cyclecare.app', $1, 'USER', 'ACTIVE', 'SUPPORT_PARTNER', 'aman_husband') RETURNING id",
      [hash]
    );
    amanId = ins.rows[0].id;
  }

  // Profile for Aman
  const checkProf = await client.query('SELECT id FROM profiles WHERE user_id = $1', [amanId]);
  if (checkProf.rows.length > 0) {
    await client.query("UPDATE profiles SET display_name = 'Aman Sharma (Husband)' WHERE user_id = $1", [amanId]);
  } else {
    await client.query("INSERT INTO profiles (user_id, display_name) VALUES ($1, 'Aman Sharma (Husband)')", [amanId]);
  }
  console.log('Aman created/updated with ID:', amanId);

  // 2. Fetch Aastha (Girl demo@cyclecare.com) and Admin
  const aastha = (await client.query("SELECT id FROM users WHERE email = 'demo@cyclecare.com'")).rows[0];
  const admin = (await client.query("SELECT id FROM users WHERE email = 'admin@cyclecare.app'")).rows[0];

  if (aastha && amanId) {
    // Check or insert connection between Aastha and Aman
    const connCheck = await client.query(
      "SELECT id FROM partner_connections WHERE (requester_id = $1 AND recipient_id = $2) OR (requester_id = $2 AND recipient_id = $1)",
      [aastha.id, amanId]
    );
    let connId;
    if (connCheck.rows.length === 0) {
      const insConn = await client.query(
        "INSERT INTO partner_connections (requester_id, recipient_id, relationship, status) VALUES ($1, $2, 'Husband', 'ACCEPTED') RETURNING id",
        [aastha.id, amanId]
      );
      connId = insConn.rows[0].id;
      console.log('Connected Aastha <-> Aman, connId:', connId);
    } else {
      connId = connCheck.rows[0].id;
      console.log('Connection already exists, connId:', connId);
    }

    // Insert follow both ways
    await client.query(
      "INSERT INTO user_follows (follower_id, following_id) VALUES ($1, $2) ON CONFLICT (follower_id, following_id) DO NOTHING",
      [aastha.id, amanId]
    );
    await client.query(
      "INSERT INTO user_follows (follower_id, following_id) VALUES ($1, $2) ON CONFLICT (follower_id, following_id) DO NOTHING",
      [amanId, aastha.id]
    );
  }

  if (aastha && admin) {
    // Check or insert connection between Aastha and Admin (CycleCare Official Help)
    const connAdmin = await client.query(
      "SELECT id FROM partner_connections WHERE (requester_id = $1 AND recipient_id = $2) OR (requester_id = $2 AND recipient_id = $1)",
      [aastha.id, admin.id]
    );
    if (connAdmin.rows.length === 0) {
      await client.query(
        "INSERT INTO partner_connections (requester_id, recipient_id, relationship, custom_relationship_label, status) VALUES ($1, $2, 'Other', 'Admin (Help)', 'ACCEPTED')",
        [aastha.id, admin.id]
      );
      console.log('Connected Aastha <-> Admin');
    }
  }

  const all = await client.query('SELECT u.id, u.email, p.display_name, u.role FROM users u LEFT JOIN profiles p ON u.id = p.user_id');
  console.log('Users:');
  console.table(all.rows);

  await client.end();
}

setupAmanAndConnections().catch(err => {
  console.error(err);
  process.exit(1);
});
