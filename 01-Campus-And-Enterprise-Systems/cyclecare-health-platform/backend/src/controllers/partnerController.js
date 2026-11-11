const supabase = require('../config/supabase');
const pool = require('../config/db');
const crypto = require('crypto');
const { sendProductCampaignNotification } = require('../services/notificationService');
const {
  determineReciprocal,
  normalizeRelationshipTag,
  validateCompatibility,
  getAmbiguityOptions
} = require('../services/relationshipMappingService');

/**
 * Fetch gender and usage_mode demographics for a user
 */
async function getUserDemographics(userId) {
  if (!userId) return { gender: null, usage_mode: null };
  try {
    const res = await pool.query(
      `SELECT u.gender AS user_gender, u.usage_mode, p.gender AS profile_gender
       FROM users u
       LEFT JOIN profiles p ON p.user_id = u.id
       WHERE u.id = $1 LIMIT 1`,
      [userId]
    );
    if (res.rows.length === 0) return { gender: null, usage_mode: null };
    const row = res.rows[0];
    return {
      gender: row.profile_gender || row.user_gender || null,
      usage_mode: row.usage_mode || null
    };
  } catch (err) {
    console.error('Error in getUserDemographics:', err);
    return { gender: null, usage_mode: null };
  }
}

const ALL_PERMISSION_TYPES = [
  'CYCLE_PHASE',
  'CYCLE_WINDOW',
  'OVULATION_WINDOW',
  'SYMPTOMS',
  'MOOD',
  'CARE_REQUESTS',
  'CARE_KIT',
  'WISHLIST',
  'REMINDERS',
  'SHOPPING',
  'DELIVERY_ADDRESS'
];

/**
 * Display Priority Ranking:
 * 1 = Husband (highest)
 * 2 = Boyfriend / Wife / Girlfriend / Partner
 * 3 = Father / Mother / Daughter / Son / Sister / Brother / Family
 * 4 = Best Friend / Guardian
 * 5 = Other / Custom
 */
function getRelationshipPriority(rel) {
  if (!rel) return 5;
  const lower = rel.toLowerCase();
  if (lower.includes('husband')) return 1;
  if (lower.includes('boyfriend') || lower.includes('partner') || lower.includes('wife') || lower.includes('girlfriend')) return 2;
  if (lower.includes('father') || lower.includes('mother') || lower.includes('daughter') || lower.includes('son') ||
      lower.includes('sister') || lower.includes('brother') || lower.includes('family') || lower.includes('parent')) return 3;
  if (lower.includes('best friend') || lower.includes('friend') || lower.includes('guardian')) return 4;
  return 5;
}

/**
 * Perspective-aware relationship label resolution
 */
function resolveRelationshipForUser(conn, userId) {
  const isRequester = conn.requester_id === userId;
  if (isRequester) {
    return conn.requester_custom_label || conn.requester_relationship || conn.custom_relationship_label || conn.relationship || 'Partner';
  } else {
    return conn.recipient_custom_label || conn.recipient_relationship || conn.custom_relationship_label || conn.relationship || 'Partner';
  }
}

/**
 * Safe display name resolver with robust fallbacks
 */
function resolveDisplayName(profile, userEmail) {
  if (profile && profile.display_name && profile.display_name.trim().length > 0) {
    return profile.display_name.trim();
  }
  if (userEmail && typeof userEmail === 'string') {
    const prefix = userEmail.split('@')[0];
    return prefix.charAt(0).toUpperCase() + prefix.slice(1);
  }
  return 'Family Member';
}

/**
 * Helper: compute initials (e.g. "Aastha Sharma" -> "AS")
 */
function getInitials(name) {
  if (!name || typeof name !== 'string') return 'CC';
  const parts = name.trim().split(/\s+/);
  if (parts.length === 1) return parts[0].substring(0, 2).toUpperCase();
  return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase();
}

/**
 * Helper: Verify active connection and granular permission
 */
async function verifyPartnerPermission(userId, connectionId, permissionType) {
  const connRes = await pool.query('SELECT * FROM partner_connections WHERE id = $1', [connectionId]);
  const conn = connRes.rows[0];

  if (!conn) {
    return { allowed: false, status: 404, message: 'Connection not found' };
  }

  if (conn.status !== 'ACCEPTED') {
    return { allowed: false, status: 403, message: `Connection is not active (status: ${conn.status})` };
  }

  if (conn.requester_id !== userId && conn.recipient_id !== userId) {
    return { allowed: false, status: 403, message: 'Unauthorized connection access' };
  }

  // The owner of the data being queried is the other participant in this connection
  const ownerId = conn.recipient_id === userId ? conn.requester_id : conn.recipient_id;

  if (!permissionType) {
    return { allowed: true, connection: conn, ownerId };
  }

  // Check granular permission row for this owner in this connection
  const permRes = await pool.query(
    `SELECT enabled FROM partner_permissions
     WHERE connection_id = $1 AND permission_type = $2
       AND (owner_id = $3 OR owner_id IS NULL)
     ORDER BY owner_id NULLS LAST LIMIT 1`,
    [connectionId, permissionType, ownerId]
  );

  const isEnabled = permRes.rows.length > 0 && permRes.rows[0].enabled === true;
  if (!isEnabled) {
    return {
      allowed: false,
      status: 403,
      message: `Access denied. Member has not granted permission for ${permissionType}.`
    };
  }

  return { allowed: true, connection: conn, ownerId };
}

// 1. Privacy-Safe Search (Never reveals cycle/health data!)
const searchPartner = async (req, res, next) => {
  try {
    let { cyclecare_id } = req.query;
    if (!cyclecare_id) {
      return res.status(400).json({ success: false, message: 'cyclecare_id is required' });
    }

    cyclecare_id = cyclecare_id.replace(/^@/, '').trim().toLowerCase();

    const { data: user, error } = await supabase
      .from('users')
      .select('id, cyclecare_id, email, profiles(display_name)')
      .eq('cyclecare_id', cyclecare_id)
      .single();

    if (error || !user) {
      return res.status(404).json({ success: false, message: 'No user found with that CycleCare ID' });
    }

    if (user.id === req.user.id) {
      return res.status(400).json({ success: false, message: 'Cannot connect with yourself' });
    }

    const safeName = resolveDisplayName(user.profiles, user.email);

    res.json({
      success: true,
      partner: {
        id: user.id,
        cyclecare_id: `@${user.cyclecare_id}`,
        display_name: safeName,
        initials: getInitials(safeName)
      }
    });
  } catch (err) {
    next(err);
  }
};

// 2. Generate Secure Invite Link
const createInvite = async (req, res, next) => {
  try {
    const userId = req.user.id;
    const token = crypto.randomBytes(16).toString('hex');
    const expiresAt = new Date(Date.now() + 7 * 24 * 60 * 60 * 1000); // 7 days

    const { data: invite, error } = await supabase
      .from('partner_invites')
      .insert([{
        owner_user_id: userId,
        invite_token: token,
        expires_at: expiresAt
      }])
      .select()
      .single();

    if (error) throw error;

    res.json({
      success: true,
      invite_token: token,
      invite_url: `cyclecare://connect/${token}`,
      expires_at: expiresAt
    });
  } catch (err) {
    next(err);
  }
};

// 3. Validate Invite Token
const validateInvite = async (req, res, next) => {
  try {
    const { token } = req.params;

    const { data: invite, error } = await supabase
      .from('partner_invites')
      .select('*, users(cyclecare_id, email, profiles(display_name))')
      .eq('invite_token', token)
      .single();

    if (error || !invite) {
      return res.status(404).json({ success: false, message: 'Invalid invite link' });
    }

    if (new Date(invite.expires_at) < new Date() || invite.used_at) {
      return res.status(410).json({ success: false, message: 'Invite link has expired or has already been used' });
    }

    const safeName = resolveDisplayName(invite.users?.profiles, invite.users?.email);

    res.json({
      success: true,
      invite: {
        owner_id: invite.owner_user_id,
        cyclecare_id: invite.users?.cyclecare_id ? `@${invite.users.cyclecare_id}` : null,
        display_name: safeName,
        initials: getInitials(safeName)
      }
    });
  } catch (err) {
    next(err);
  }
};

// 4. Send Connection Request with Perspective Tagging
const sendConnectionRequest = async (req, res, next) => {
  try {
    const requesterId = req.user.id;
    let { recipient_id, recipient_email, cyclecare_id, invite_token, relationship, custom_label, requester_relationship, recipient_relationship } = req.body;

    // Resolve recipient ID if email, handle or token provided
    if (!recipient_id && recipient_email) {
      const cleanEmail = recipient_email.trim().toLowerCase();
      const userRes = await pool.query('SELECT id FROM users WHERE LOWER(email) = $1 LIMIT 1', [cleanEmail]);
      if (userRes.rows[0]) recipient_id = userRes.rows[0].id;
    } else if (!recipient_id && cyclecare_id) {
      const cleanId = cyclecare_id.replace(/^@/, '').trim().toLowerCase();
      const userRes = await pool.query('SELECT id FROM users WHERE LOWER(cyclecare_id) = $1 LIMIT 1', [cleanId]);
      if (userRes.rows[0]) recipient_id = userRes.rows[0].id;
    } else if (!recipient_id && invite_token) {
      const invRes = await pool.query('SELECT owner_user_id FROM partner_invites WHERE invite_token = $1 LIMIT 1', [invite_token]);
      if (invRes.rows[0]) recipient_id = invRes.rows[0].owner_user_id;
    }

    if (!recipient_id) {
      return res.status(400).json({ success: false, message: 'Recipient partner not found' });
    }

    if (recipient_id === requesterId) {
      return res.status(400).json({ success: false, message: 'Cannot connect to your own account' });
    }

    const actorDemo = await getUserDemographics(requesterId);
    const targetDemo = await getUserDemographics(recipient_id);

    let cleanRequesterRel = 'Partner';
    let cleanRecipientRel = 'Partner';
    let cleanRel = 'Partner';
    const cleanCustom = (custom_label || '').trim();

    try {
      const tagToAssign = relationship || requester_relationship || 'Partner';
      let explicitTargetReciprocal = recipient_relationship;
      if (requester_relationship && relationship && normalizeRelationshipTag(requester_relationship) !== normalizeRelationshipTag(relationship)) {
        if (validateCompatibility(relationship, requester_relationship).valid) {
          explicitTargetReciprocal = requester_relationship;
        }
      }

      const mapping = determineReciprocal({
        assignedTag: tagToAssign,
        actorGender: actorDemo.gender,
        actorUsageMode: actorDemo.usage_mode,
        targetGender: targetDemo.gender,
        targetUsageMode: targetDemo.usage_mode,
        explicitReciprocal: explicitTargetReciprocal
      });
      cleanRequesterRel = mapping.assigned;
      cleanRecipientRel = mapping.reciprocal;
      cleanRel = mapping.assigned;
    } catch (err) {
      if (err.code === 'INCOMPATIBLE_RELATIONSHIP' || err.code === 'RECIPROCAL_RELATIONSHIP_AMBIGUOUS') {
        return res.status(err.statusCode || 400).json({
          success: false,
          error: err.code,
          message: err.message,
          options: err.options || []
        });
      }
      throw err;
    }

    // Check existing connection pair
    const checkRes = await pool.query(
      `SELECT * FROM partner_connections 
       WHERE (requester_id = $1 AND recipient_id = $2) 
          OR (requester_id = $2 AND recipient_id = $1)`,
      [requesterId, recipient_id]
    );

    const existing = checkRes.rows[0];

    if (existing) {
      if (existing.status === 'ACCEPTED') {
        return res.status(400).json({ success: false, message: 'You are already connected with this person' });
      }
      if (existing.status === 'PENDING') {
        return res.status(400).json({ success: false, message: 'A connection request is already pending' });
      }
      if (existing.status === 'BLOCKED') {
        return res.status(403).json({ success: false, message: 'Unable to connect with this user' });
      }

      // Reopen revoked or declined connection
      const renewRes = await pool.query(
        `UPDATE partner_connections 
         SET status = 'PENDING', requester_id = $1, recipient_id = $2,
             relationship = $3, custom_relationship_label = $4,
             requester_relationship = $5, recipient_relationship = $6, requester_custom_label = $4,
             updated_at = NOW()
         WHERE id = $7 RETURNING *`,
        [requesterId, recipient_id, cleanRel, cleanCustom, cleanRequesterRel, cleanRecipientRel, existing.id]
      );

      // Audit trail
      await pool.query(
        `INSERT INTO sharing_audit_events (connection_id, actor_id, event_type, target_user_id, metadata)
         VALUES ($1, $2, 'REQUEST_SENT', $3, $4)`,
        [existing.id, requesterId, recipient_id, JSON.stringify({ relationship: cleanRel, custom_label: cleanCustom })]
      );

      return res.json({ success: true, message: 'Connection request sent successfully', connection: renewRes.rows[0] });
    }

    const insertRes = await pool.query(
      `INSERT INTO partner_connections 
       (requester_id, recipient_id, status, relationship, custom_relationship_label, requester_relationship, recipient_relationship, requester_custom_label)
       VALUES ($1, $2, 'PENDING', $3, $4, $5, $6, $4) RETURNING *`,
      [requesterId, recipient_id, cleanRel, cleanCustom, cleanRequesterRel, cleanRecipientRel]
    );

    const conn = insertRes.rows[0];

    // Audit trail
    await pool.query(
      `INSERT INTO sharing_audit_events (connection_id, actor_id, event_type, target_user_id, metadata)
       VALUES ($1, $2, 'REQUEST_SENT', $3, $4)`,
      [conn.id, requesterId, recipient_id, JSON.stringify({ relationship: cleanRel, custom_label: cleanCustom })]
    );

    // Send privacy-safe in-app notification
    try {
      await supabase.from('notifications').insert([{
        user_id: recipient_id,
        title: 'New Family & Partner Connection Request',
        body: `Someone would like to connect with you as ${cleanCustom || cleanRel}.`,
        type: 'PARTNER_REQUEST'
      }]);
    } catch (_) {}

    res.status(201).json({ success: true, message: 'Connection request sent', connection: conn });
  } catch (err) {
    next(err);
  }
};

// 5. List Requests and Connections with Priority Ranking and Multi-Member Support
const listRequests = async (req, res, next) => {
  try {
    const userId = req.user.id;

    const query = `
      SELECT pc.*,
        ru.cyclecare_id AS requester_cyclecare_id, ru.email AS requester_email,
        rp.display_name AS requester_display_name, rp.profile_image AS requester_avatar,
        cu.cyclecare_id AS recipient_cyclecare_id, cu.email AS recipient_email,
        cp.display_name AS recipient_display_name, cp.profile_image AS recipient_avatar
      FROM partner_connections pc
      LEFT JOIN users ru ON pc.requester_id = ru.id
      LEFT JOIN profiles rp ON pc.requester_id = rp.user_id
      LEFT JOIN users cu ON pc.recipient_id = cu.id
      LEFT JOIN profiles cp ON pc.recipient_id = cp.user_id
      WHERE pc.requester_id = $1 OR pc.recipient_id = $1
      ORDER BY pc.updated_at DESC
    `;

    const result = await pool.query(query, [userId]);
    const connections = result.rows;

    const incoming = [];
    const outgoing = [];
    const allActive = [];
    const revokedList = [];

    // Fetch active permissions for user
    const permsRes = await pool.query(
      `SELECT connection_id, permission_type, enabled, owner_id FROM partner_permissions
       WHERE connection_id = ANY($1)`,
      [connections.map(c => c.id).filter(Boolean)]
    );

    const permsByConn = {};
    permsRes.rows.forEach(p => {
      if (!permsByConn[p.connection_id]) permsByConn[p.connection_id] = {};
      permsByConn[p.connection_id][p.permission_type] = p.enabled;
    });

    for (const c of connections) {
      const isRecipient = c.recipient_id === userId;
      const otherUserId = isRecipient ? c.requester_id : c.recipient_id;
      const otherHandle = isRecipient ? c.requester_cyclecare_id : c.recipient_cyclecare_id;
      const otherEmail = isRecipient ? c.requester_email : c.recipient_email;
      const otherDisplayName = isRecipient ? c.requester_display_name : c.recipient_display_name;
      const otherAvatar = isRecipient ? c.requester_avatar : c.recipient_avatar;

      const safeName = resolveDisplayName({ display_name: otherDisplayName }, otherEmail);
      const relationshipLabel = resolveRelationshipForUser(c, userId);
      const priorityRank = getRelationshipPriority(relationshipLabel);

      const connData = {
        id: c.id,
        status: c.status,
        relationship: relationshipLabel,
        resolved_relationship: relationshipLabel,
        priority_rank: priorityRank,
        is_primary_partner: !!c.is_primary_partner,
        created_at: c.created_at,
        accepted_at: c.accepted_at,
        updated_at: c.updated_at,
        partner: {
          id: otherUserId,
          cyclecare_id: otherHandle ? `@${otherHandle}` : null,
          display_name: safeName,
          avatar_url: otherAvatar || null,
          initials: getInitials(safeName)
        },
        partner_profile: {
          id: otherUserId,
          cyclecare_id: otherHandle ? `@${otherHandle}` : null,
          display_name: safeName,
          avatar_url: otherAvatar || null,
          initials: getInitials(safeName)
        },
        permissions_summary: permsByConn[c.id] || {}
      };

      if (c.status === 'ACCEPTED') {
        allActive.push(connData);
      } else if (c.status === 'PENDING') {
        if (isRecipient) incoming.push(connData);
        else outgoing.push(connData);
      } else if (['REVOKED', 'DECLINED', 'BLOCKED'].includes(c.status)) {
        revokedList.push(connData);
      }
    }

    // Sort active connections by Priority Rank ASC (Husband rank 1, Partner rank 2, Family rank 3...), then updated_at DESC
    allActive.sort((a, b) => {
      if (a.priority_rank !== b.priority_rank) return a.priority_rank - b.priority_rank;
      return new Date(b.updated_at) - new Date(a.updated_at);
    });

    // Primary partner is the top priority connection (Husband, Partner)
    const primaryPartner = allActive.length > 0 && allActive[0].priority_rank <= 2 ? allActive[0] : null;
    const familyMembers = primaryPartner ? allActive.slice(1) : allActive;

    res.json({
      success: true,
      primary_partner: primaryPartner,
      family_members: familyMembers,
      all_active: allActive,
      incoming,
      outgoing,
      revoked: revokedList,
      total_active_count: allActive.length
    });
  } catch (err) {
    next(err);
  }
};

// 6. Accept Connection Request (with optional reciprocal relationship label)
const acceptRequest = async (req, res, next) => {
  try {
    const userId = req.user.id;
    const connectionId = req.params.id;
    const { reciprocal_relationship, custom_label } = req.body || {};

    const connRes = await pool.query('SELECT * FROM partner_connections WHERE id = $1', [connectionId]);
    const conn = connRes.rows[0];

    if (!conn) {
      return res.status(404).json({ success: false, message: 'Request not found' });
    }

    if (conn.recipient_id !== userId) {
      return res.status(403).json({ success: false, message: 'Only the recipient can accept this request' });
    }

    let cleanRel = conn.recipient_relationship || 'Partner';
    if (reciprocal_relationship) {
      const compat = validateCompatibility(conn.requester_relationship || conn.relationship || 'Partner', reciprocal_relationship);
      if (!compat.valid) {
        return res.status(400).json({ success: false, message: compat.reason });
      }
      cleanRel = normalizeRelationshipTag(reciprocal_relationship);
    } else if (!cleanRel || cleanRel === 'Partner') {
      const recipientDemo = await getUserDemographics(userId);
      const requesterDemo = await getUserDemographics(conn.requester_id);
      const derived = determineReciprocal({
        assignedTag: conn.requester_relationship || conn.relationship || 'Partner',
        actorGender: requesterDemo.gender,
        actorUsageMode: requesterDemo.usage_mode,
        targetGender: recipientDemo.gender,
        targetUsageMode: recipientDemo.usage_mode
      });
      cleanRel = derived.reciprocal;
    }
    const cleanCustom = (custom_label || '').trim();

    const updateRes = await pool.query(
      `UPDATE partner_connections 
       SET status = 'ACCEPTED', accepted_at = NOW(), updated_at = NOW(),
           recipient_relationship = $1, recipient_custom_label = $2
       WHERE id = $3 RETURNING *`,
      [cleanRel, cleanCustom, connectionId]
    );

    const updated = updateRes.rows[0];

    // Initialize all granular permissions to FALSE (Default: ALL OFF, privacy-first)
    for (const type of ALL_PERMISSION_TYPES) {
      // For both user directions
      await pool.query(
        `INSERT INTO partner_permissions (connection_id, permission_type, owner_id, enabled, updated_at)
         VALUES ($1, $2, $3, false, NOW())
         ON CONFLICT (connection_id, permission_type, COALESCE(owner_id, '00000000-0000-0000-0000-000000000000'::uuid))
         DO NOTHING`,
        [connectionId, type, userId]
      );
      await pool.query(
        `INSERT INTO partner_permissions (connection_id, permission_type, owner_id, enabled, updated_at)
         VALUES ($1, $2, $3, false, NOW())
         ON CONFLICT (connection_id, permission_type, COALESCE(owner_id, '00000000-0000-0000-0000-000000000000'::uuid))
         DO NOTHING`,
        [connectionId, type, conn.requester_id]
      );
    }

    // Audit trail
    await pool.query(
      `INSERT INTO sharing_audit_events (connection_id, actor_id, event_type, target_user_id, metadata)
       VALUES ($1, $2, 'ACCEPTED', $3, $4)`,
      [connectionId, userId, conn.requester_id, JSON.stringify({ reciprocal_relationship: cleanRel, custom_label: cleanCustom })]
    );

    // Notify requester
    try {
      await supabase.from('notifications').insert([{
        user_id: conn.requester_id,
        title: 'Connection Accepted! 🤝',
        body: 'You are now connected on CycleCare. Each member controls what they choose to share.',
        type: 'PARTNER_ACCEPTED'
      }]);
    } catch (_) {}

    res.json({
      success: true,
      message: 'Connection accepted. All sharing permissions default to OFF.',
      connection: updated
    });
  } catch (err) {
    next(err);
  }
};

// 7. Decline Connection Request
const declineRequest = async (req, res, next) => {
  try {
    const userId = req.user.id;
    const connectionId = req.params.id;

    const connRes = await pool.query('SELECT * FROM partner_connections WHERE id = $1', [connectionId]);
    const conn = connRes.rows[0];

    if (!conn) {
      return res.status(404).json({ success: false, message: 'Request not found' });
    }

    if (conn.recipient_id !== userId) {
      return res.status(403).json({ success: false, message: 'Only the recipient can decline this request' });
    }

    await pool.query(
      `UPDATE partner_connections 
       SET status = 'DECLINED', declined_at = NOW(), updated_at = NOW() 
       WHERE id = $1`,
      [connectionId]
    );

    // Audit trail
    await pool.query(
      `INSERT INTO sharing_audit_events (connection_id, actor_id, event_type, target_user_id)
       VALUES ($1, $2, 'DECLINED', $3)`,
      [connectionId, userId, conn.requester_id]
    );

    res.json({ success: true, message: 'Connection request declined' });
  } catch (err) {
    next(err);
  }
};

// 8. Disconnect / Revoke Connection (Immediately Blocks Access)
const revokeConnection = async (req, res, next) => {
  try {
    const userId = req.user.id;
    const connectionId = req.params.connectionId;

    const connRes = await pool.query(
      `SELECT * FROM partner_connections 
       WHERE id = $1 AND (requester_id = $2 OR recipient_id = $2)`,
      [connectionId, userId]
    );
    const conn = connRes.rows[0];

    if (!conn) {
      return res.status(404).json({ success: false, message: 'Connection not found' });
    }

    const otherUserId = conn.requester_id === userId ? conn.recipient_id : conn.requester_id;

    await pool.query(
      `UPDATE partner_connections 
       SET status = 'REVOKED', revoked_at = NOW(), updated_at = NOW() 
       WHERE id = $1`,
      [connectionId]
    );

    // Immediately disable all permissions
    await pool.query(
      `UPDATE partner_permissions SET enabled = false, updated_at = NOW() 
       WHERE connection_id = $1`,
      [connectionId]
    );

    // Audit trail
    await pool.query(
      `INSERT INTO sharing_audit_events (connection_id, actor_id, event_type, target_user_id)
       VALUES ($1, $2, 'REVOKED', $3)`,
      [connectionId, userId, otherUserId]
    );

    res.json({ success: true, message: 'Connection disconnected and access revoked immediately.' });
  } catch (err) {
    next(err);
  }
};

// 9. Block User
const blockPartner = async (req, res, next) => {
  try {
    const userId = req.user.id;
    const connectionId = req.params.connectionId;

    const connRes = await pool.query(
      `SELECT * FROM partner_connections 
       WHERE id = $1 AND (requester_id = $2 OR recipient_id = $2)`,
      [connectionId, userId]
    );
    const conn = connRes.rows[0];

    if (!conn) {
      return res.status(404).json({ success: false, message: 'Connection not found' });
    }

    const otherUserId = conn.requester_id === userId ? conn.recipient_id : conn.requester_id;

    await pool.query(
      `UPDATE partner_connections SET status = 'BLOCKED', updated_at = NOW() WHERE id = $1`,
      [connectionId]
    );
    await pool.query(
      `UPDATE partner_permissions SET enabled = false, updated_at = NOW() WHERE connection_id = $1`,
      [connectionId]
    );

    // Audit trail
    await pool.query(
      `INSERT INTO sharing_audit_events (connection_id, actor_id, event_type, target_user_id)
       VALUES ($1, $2, 'BLOCKED', $3)`,
      [connectionId, userId, otherUserId]
    );

    res.json({ success: true, message: 'User blocked and connection terminated' });
  } catch (err) {
    next(err);
  }
};

// 10. Update Relationship Perspective (Bidirectional Reciprocal Persistence)
const updateRelationship = async (req, res, next) => {
  try {
    const userId = req.user.id;
    const connectionId = req.params.connectionId;
    const { relationship, custom_label, reciprocal_relationship } = req.body;

    if (!relationship && !custom_label) {
      return res.status(400).json({ success: false, message: 'relationship or custom_label is required' });
    }

    const connRes = await pool.query(
      `SELECT * FROM partner_connections 
       WHERE id = $1 AND (requester_id = $2 OR recipient_id = $2)`,
      [connectionId, userId]
    );
    const conn = connRes.rows[0];

    if (!conn) {
      return res.status(404).json({ success: false, message: 'Connection not found' });
    }

    const isRequester = conn.requester_id === userId;
    const otherUserId = isRequester ? conn.recipient_id : conn.requester_id;

    const actorDemo = await getUserDemographics(userId);
    const targetDemo = await getUserDemographics(otherUserId);

    const rawTag = relationship || custom_label || 'Partner';
    let mapping;
    try {
      mapping = determineReciprocal({
        assignedTag: rawTag,
        actorGender: actorDemo.gender,
        actorUsageMode: actorDemo.usage_mode,
        targetGender: targetDemo.gender,
        targetUsageMode: targetDemo.usage_mode,
        explicitReciprocal: reciprocal_relationship
      });
    } catch (err) {
      if (err.code === 'INCOMPATIBLE_RELATIONSHIP' || err.code === 'RECIPROCAL_RELATIONSHIP_AMBIGUOUS') {
        return res.status(err.statusCode || 400).json({
          success: false,
          error: err.code,
          message: err.message,
          options: err.options || []
        });
      }
      throw err;
    }

    const cleanAssigned = mapping.assigned;
    const cleanReciprocal = mapping.reciprocal;
    const cleanCustom = (custom_label || '').trim();

    if (isRequester) {
      await pool.query(
        `UPDATE partner_connections 
         SET requester_relationship = $1, recipient_relationship = $2,
             requester_custom_label = $3,
             relationship = $1, custom_relationship_label = $3, updated_at = NOW()
         WHERE id = $4`,
        [cleanAssigned, cleanReciprocal, cleanCustom || null, connectionId]
      );
    } else {
      await pool.query(
        `UPDATE partner_connections 
         SET recipient_relationship = $1, requester_relationship = $2,
             recipient_custom_label = $3,
             relationship = $2, updated_at = NOW()
         WHERE id = $4`,
        [cleanAssigned, cleanReciprocal, cleanCustom || null, connectionId]
      );
    }

    // Audit trail
    await pool.query(
      `INSERT INTO sharing_audit_events (connection_id, actor_id, event_type, target_user_id, metadata)
       VALUES ($1, $2, 'RELATIONSHIP_UPDATED', $3, $4)`,
      [connectionId, userId, otherUserId, JSON.stringify({
        assigned: cleanAssigned,
        reciprocal: cleanReciprocal,
        custom_label: cleanCustom
      })]
    );

    res.json({
      success: true,
      message: `Relationship updated to "${cleanCustom || cleanAssigned}" (reciprocal: "${cleanReciprocal}")`,
      relationship: cleanAssigned,
      reciprocal_relationship: cleanReciprocal,
      custom_label: cleanCustom
    });
  } catch (err) {
    next(err);
  }
};

// 11. Get Permissions Matrix (For data owner or viewer)
const getPermissions = async (req, res, next) => {
  try {
    const userId = req.user.id;
    const connectionId = req.params.connectionId;
    const queryOwnerId = req.query.owner_id;

    const authCheck = await verifyPartnerPermission(userId, connectionId, null);
    if (!authCheck.allowed) {
      return res.status(authCheck.status).json({ success: false, message: authCheck.message, error: authCheck.message });
    }

    // Target owner: if queryOwnerId specified, use it; otherwise default to logged in user (what I share)
    const targetOwner = queryOwnerId || userId;

    const permRes = await pool.query(
      `SELECT permission_type, enabled, updated_at FROM partner_permissions
       WHERE connection_id = $1 AND (owner_id = $2 OR owner_id IS NULL)`,
      [connectionId, targetOwner]
    );

    const permissionMap = {};
    ALL_PERMISSION_TYPES.forEach(t => { permissionMap[t] = false; });
    permRes.rows.forEach(p => { permissionMap[p.permission_type] = p.enabled; });

    res.json({
      success: true,
      connection_id: connectionId,
      owner_id: targetOwner,
      is_owner: targetOwner === userId,
      permissions: permissionMap,
      raw: permRes.rows
    });
  } catch (err) {
    next(err);
  }
};

// 12. Update Permissions (Data Owner Opt-in / Opt-out with Immediate Effect)
const updatePermissions = async (req, res, next) => {
  try {
    const userId = req.user.id;
    const connectionId = req.params.connectionId;
    const { permissions } = req.body;

    if (!permissions || typeof permissions !== 'object') {
      return res.status(400).json({ success: false, message: 'Permissions object required', error: 'Permissions object required' });
    }

    const authCheck = await verifyPartnerPermission(userId, connectionId, null);
    if (!authCheck.allowed) {
      return res.status(authCheck.status).json({ success: false, message: authCheck.message, error: authCheck.message });
    }

    // The user calling this IS the data owner (userId)
    for (const [permType, isEnabled] of Object.entries(permissions)) {
      if (ALL_PERMISSION_TYPES.includes(permType)) {
        await pool.query(
          `INSERT INTO partner_permissions (connection_id, permission_type, owner_id, enabled, updated_at)
           VALUES ($1, $2, $3, $4, NOW())
           ON CONFLICT (connection_id, permission_type, COALESCE(owner_id, '00000000-0000-0000-0000-000000000000'::uuid))
           DO UPDATE SET enabled = EXCLUDED.enabled, updated_at = NOW()`,
          [connectionId, permType, userId, !!isEnabled]
        );
      }
    }

    // Audit trail
    await pool.query(
      `INSERT INTO sharing_audit_events (connection_id, actor_id, event_type, target_user_id, metadata)
       VALUES ($1, $2, 'PERMISSIONS_UPDATED', $3, $4)`,
      [connectionId, userId, authCheck.ownerId, JSON.stringify(permissions)]
    );

    res.json({ success: true, message: 'Sharing settings updated successfully', permissions, updated: permissions });
  } catch (err) {
    next(err);
  }
};

// 13. Permitted Member Status (Multi-Member, granularly authorized cycle & health data)
const getMemberStatus = async (req, res, next) => {
  try {
    const userId = req.user.id;
    const connectionId = req.params.connectionId;

    // Verify connection is ACCEPTED and user is participant
    const authCheck = await verifyPartnerPermission(userId, connectionId, null);
    if (!authCheck.allowed) {
      return res.status(authCheck.status).json({ success: false, message: authCheck.message, error: authCheck.message });
    }

    const memberId = authCheck.ownerId; // Data owner
    const conn = authCheck.connection;
    const relationshipLabel = resolveRelationshipForUser(conn, userId);

    // Fetch member's profile
    const memberProfRes = await pool.query(
      `SELECT u.email, u.cyclecare_id, p.display_name, p.profile_image AS avatar_url 
       FROM users u LEFT JOIN profiles p ON u.id = p.user_id 
       WHERE u.id = $1`,
      [memberId]
    );
    const memberUser = memberProfRes.rows[0];
    const memberName = resolveDisplayName(memberUser, memberUser?.email);

    // Fetch all permissions granted by memberId in this connection
    const permRes = await pool.query(
      `SELECT permission_type, enabled FROM partner_permissions
       WHERE connection_id = $1 AND (owner_id = $2 OR owner_id IS NULL)`,
      [connectionId, memberId]
    );

    const permMap = {};
    ALL_PERMISSION_TYPES.forEach(t => { permMap[t] = false; });
    permRes.rows.forEach(p => { permMap[p.permission_type] = p.enabled; });

    // Fetch member's cycle settings
    const csRes = await pool.query('SELECT * FROM cycle_settings WHERE user_id = $1', [memberId]);
    const settings = csRes.rows[0] || { cycle_length: 28, period_duration: 5 };

    // Fetch member's latest period log
    const plRes = await pool.query(
      'SELECT * FROM period_logs WHERE user_id = $1 ORDER BY start_date DESC LIMIT 1',
      [memberId]
    );
    const latestPeriod = plRes.rows[0];

    // Compute cycle calculations
    const cycleLength = settings.cycle_length || 28;
    const periodDuration = settings.period_duration || 5;
    const lastStart = latestPeriod ? new Date(latestPeriod.start_date) : new Date(Date.now() - 14 * 24 * 60 * 60 * 1000);
    const now = new Date();
    const daysSinceStart = Math.max(0, Math.floor((now - lastStart) / (1000 * 60 * 60 * 24)));
    const currentDayInCycle = (daysSinceStart % cycleLength) + 1;

    const nextEstimatedStart = new Date(lastStart.getTime() + cycleLength * 24 * 60 * 60 * 1000);
    const nextEstimatedEnd = new Date(nextEstimatedStart.getTime() + (periodDuration - 1) * 24 * 60 * 60 * 1000);
    const daysUntilPeriod = Math.ceil((nextEstimatedStart - now) / (1000 * 60 * 60 * 24));

    // Ovulation window estimation (approx cycleLength - 14)
    const ovulationDay = Math.max(1, cycleLength - 14);
    const ovulationDate = new Date(lastStart.getTime() + (ovulationDay - 1) * 24 * 60 * 60 * 1000);
    const fertileStart = new Date(ovulationDate.getTime() - 4 * 24 * 60 * 60 * 1000);
    const fertileEnd = new Date(ovulationDate.getTime() + 1 * 24 * 60 * 60 * 1000);

    // Determine current phase
    let phaseName = 'Follicular Phase';
    if (currentDayInCycle <= periodDuration) {
      phaseName = 'Menstrual Phase';
    } else if (currentDayInCycle >= ovulationDay - 1 && currentDayInCycle <= ovulationDay + 1) {
      phaseName = 'Ovulation Window';
    } else if (currentDayInCycle > ovulationDay + 1) {
      phaseName = 'Luteal Phase';
    }

    const disclaimerText = 'Predictions are estimates for comfort, preparation, and mutual care only, not medical diagnosis.';

    // Build permission-gated fields
    const responsePayload = {
      success: true,
      connection_id: connectionId,
      relationship: relationshipLabel,
      member: {
        id: memberId,
        display_name: memberName,
        cyclecare_id: memberUser?.cyclecare_id ? `@${memberUser.cyclecare_id}` : null,
        initials: getInitials(memberName)
      },
      permissions: permMap,
      disclaimer: disclaimerText,
      last_updated: new Date().toISOString()
    };

    // 1. CYCLE_PHASE
    if (permMap.CYCLE_PHASE) {
      responsePayload.cycle_phase = {
        permitted: true,
        phase: phaseName,
        current_day: currentDayInCycle,
        cycle_length: cycleLength,
        description: `Day ${currentDayInCycle} of ${cycleLength} • ${phaseName}`,
        medical_disclaimer: disclaimerText
      };
    } else {
      responsePayload.cycle_phase = { permitted: false, status: 'NOT_SHARED', medical_disclaimer: disclaimerText };
    }

    // 2. CYCLE_WINDOW
    if (permMap.CYCLE_WINDOW) {
      responsePayload.cycle_window = {
        permitted: true,
        estimated_start: nextEstimatedStart.toISOString().split('T')[0],
        estimated_end: nextEstimatedEnd.toISOString().split('T')[0],
        days_until_period: daysUntilPeriod > 0 ? daysUntilPeriod : 0,
        period_status: daysUntilPeriod <= 0 ? 'Window Active' : `Approaching in ~${daysUntilPeriod} days`,
        support_tip: daysUntilPeriod <= 3
          ? 'Comfort window is approaching. Perfect time to prepare soothing care essentials!'
          : 'Normal cycle support window active.'
      };
    } else {
      responsePayload.cycle_window = { permitted: false, status: 'NOT_SHARED' };
    }

    // 3. OVULATION_WINDOW
    if (permMap.OVULATION_WINDOW) {
      responsePayload.ovulation_window = {
        permitted: true,
        estimated_ovulation: ovulationDate.toISOString().split('T')[0],
        fertile_window_start: fertileStart.toISOString().split('T')[0],
        fertile_window_end: fertileEnd.toISOString().split('T')[0]
      };
    } else {
      responsePayload.ovulation_window = { permitted: false, status: 'NOT_SHARED' };
    }

    // 4. SYMPTOMS
    if (permMap.SYMPTOMS) {
      const symRes = await pool.query(
        `SELECT symptom_name, severity, log_date FROM symptom_logs 
         WHERE user_id = $1 ORDER BY log_date DESC LIMIT 5`,
        [memberId]
      );
      responsePayload.symptoms = {
        permitted: true,
        items: symRes.rows.map(s => s.symptom_name),
        recent_symptoms: symRes.rows.map(s => s.symptom_name)
      };
    } else {
      responsePayload.symptoms = { permitted: false, status: 'NOT_SHARED', items: [] };
    }

    // 5. CARE_REQUESTS
    if (permMap.CARE_REQUESTS || permMap.CARE_KIT) {
      const crRes = await pool.query(
        `SELECT content, metadata, created_at FROM circle_messages 
         WHERE connection_id = $1 AND message_type = 'CARE_REQUEST'
         ORDER BY created_at DESC LIMIT 3`,
        [connectionId]
      );
      responsePayload.care_requests = {
        permitted: true,
        active_requests: crRes.rows
      };
    } else {
      responsePayload.care_requests = { permitted: false, status: 'NOT_SHARED' };
    }

    // 6. REMINDERS
    if (permMap.REMINDERS) {
      responsePayload.reminders = {
        permitted: true,
        notes: 'Reminders enabled by member'
      };
    } else {
      responsePayload.reminders = { permitted: false, status: 'NOT_SHARED' };
    }

    responsePayload.status = {
      cycle_phase: responsePayload.cycle_phase,
      cycle_window: responsePayload.cycle_window,
      ovulation_window: responsePayload.ovulation_window,
      symptoms: responsePayload.symptoms,
      care_requests: responsePayload.care_requests,
      reminders: responsePayload.reminders
    };

    // Audit trail (Data Access)
    await pool.query(
      `INSERT INTO sharing_audit_events (connection_id, actor_id, event_type, target_user_id, metadata)
       VALUES ($1, $2, 'DATA_ACCESSED', $3, $4)`,
      [connectionId, userId, memberId, JSON.stringify({ permitted_fields: Object.keys(permMap).filter(k => permMap[k]) })]
    );

    res.json(responsePayload);
  } catch (err) {
    next(err);
  }
};

// 14. Permitted Data Access: Shared Cycle Window (Preserved existing endpoint)
const getSharedCycle = async (req, res, next) => {
  return getMemberStatus(req, res, next);
};

// 15. Permitted Data Access: Shared Care Kit (Requires CARE_KIT=ON)
const getSharedCareKit = async (req, res, next) => {
  try {
    const userId = req.user.id;
    const connectionId = req.params.connectionId;

    const check = await verifyPartnerPermission(userId, connectionId, 'CARE_KIT');
    if (!check.allowed) {
      return res.status(check.status).json({ success: false, message: check.message });
    }

    const partnerId = check.ownerId;
    const { data: kits, error } = await supabase
      .from('care_kits')
      .select('*, care_kit_items(*, products(*))')
      .eq('user_id', partnerId);

    if (error) throw error;
    res.json({ success: true, care_kits: kits || [] });
  } catch (err) {
    next(err);
  }
};

// 16. Permitted Data Access: Shared Wishlist (Requires WISHLIST=ON)
const getSharedWishlist = async (req, res, next) => {
  try {
    const userId = req.user.id;
    const connectionId = req.params.connectionId;

    const check = await verifyPartnerPermission(userId, connectionId, 'WISHLIST');
    if (!check.allowed) {
      return res.status(check.status).json({ success: false, message: check.message });
    }

    const partnerId = check.ownerId;
    const { data: wishlist, error } = await supabase
      .from('wishlist')
      .select('*, products(*)')
      .eq('user_id', partnerId);

    if (error) throw error;
    res.json({ success: true, wishlist: wishlist || [] });
  } catch (err) {
    next(err);
  }
};

// 17. Create Care Package Order
const createCarePackage = async (req, res, next) => {
  try {
    const buyerId = req.user.id;
    const connectionId = req.params.connectionId;
    const { items, message, delivery_address } = req.body;

    const check = await verifyPartnerPermission(buyerId, connectionId, 'SHOPPING');
    if (!check.allowed) {
      return res.status(check.status).json({ success: false, message: check.message });
    }

    const recipientId = check.ownerId;

    if (!items || !Array.isArray(items) || items.length === 0) {
      return res.status(400).json({ success: false, message: 'Care package must contain items' });
    }

    let totalAmount = 0;
    items.forEach(it => {
      totalAmount += (it.price || 199) * (it.quantity || 1);
    });

    const { data: order, error } = await supabase
      .from('orders')
      .insert([{
        user_id: buyerId,
        buyer_id: buyerId,
        recipient_user_id: recipientId,
        total_amount: totalAmount,
        status: 'PAID',
        care_package_message: message || "Thinking of you. Take care! ❤️",
        delivery_address: delivery_address || 'Partner Saved Address'
      }])
      .select()
      .single();

    if (error) throw error;

    try {
      await supabase.from('notifications').insert([{
        user_id: recipientId,
        title: 'Care Package Sent To You! 🎁',
        body: `Your family member sent you a care package: "${message || 'Take care. I am here for you.'}"`,
        type: 'CARE_PACKAGE_RECEIVED'
      }]);
    } catch (_) {}

    res.status(201).json({
      success: true,
      message: 'Care package ordered successfully!',
      order
    });
  } catch (err) {
    next(err);
  }
};

// 18. Permitted Data Access: Shared Address (Requires DELIVERY_ADDRESS=ON)
const getSharedAddress = async (req, res, next) => {
  try {
    const userId = req.user.id;
    const connectionId = req.params.connectionId;

    const check = await verifyPartnerPermission(userId, connectionId, 'DELIVERY_ADDRESS');
    if (!check.allowed) {
      return res.status(check.status).json({ success: false, message: check.message });
    }

    const partnerId = check.ownerId;
    const { data: addr } = await supabase
      .from('shared_addresses')
      .select('*')
      .eq('owner_user_id', partnerId)
      .eq('is_active', true)
      .limit(1)
      .single();

    res.json({ success: true, address: addr || null });
  } catch (err) {
    next(err);
  }
};

// 19. Get Connection Audit Trail
const getAuditTrail = async (req, res, next) => {
  try {
    const userId = req.user.id;
    const connectionId = req.params.connectionId;

    const authCheck = await verifyPartnerPermission(userId, connectionId, null);
    if (!authCheck.allowed) {
      return res.status(authCheck.status).json({ success: false, message: authCheck.message });
    }

    const auditRes = await pool.query(
      `SELECT id, event_type, actor_id, metadata, created_at 
       FROM sharing_audit_events 
       WHERE connection_id = $1 
       ORDER BY created_at DESC LIMIT 30`,
      [connectionId]
    );

    res.json({ success: true, events: auditRes.rows });
  } catch (err) {
    next(err);
  }
};

module.exports = {
  searchPartner,
  createInvite,
  validateInvite,
  sendConnectionRequest,
  listRequests,
  acceptRequest,
  declineRequest,
  revokeConnection,
  blockPartner,
  updateRelationship,
  getPermissions,
  updatePermissions,
  getMemberStatus,
  getSharedCycle,
  getSharedCareKit,
  getSharedWishlist,
  createCarePackage,
  getSharedAddress,
  getAuditTrail
};
