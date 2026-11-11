const pool = require('../config/db');
const { sendChatPushNotification } = require('../services/notificationService');
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
    return { gender: null, usage_mode: null };
  }
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

// Curated Quick Care Items for In-Chat Assistance
const QUICK_CARE_ITEMS = [
  {
    id: "care-pad-01",
    name: "Whisper Ultra Clean Sanitary Pads (XL)",
    category: "Sanitary & Hygiene",
    price: 199,
    image_url: "https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?auto=format&fit=crop&w=600&q=80",
    description: "Discreet gentle organic cotton pads with wings"
  },
  {
    id: "care-patch-02",
    name: "Sirona Feminine Pain Relief Heating Patch",
    category: "Pain Relief",
    price: 299,
    image_url: "https://images.unsplash.com/photo-1583947215259-38e31be8751f?auto=format&fit=crop&w=600&q=80",
    description: "Up to 8 hours of continuous soothing cramp warmth"
  },
  {
    id: "009f4b12-2efa-4e28-8c1a-4f872e955fb7",
    name: "CycleCare Herbal Cramp Relief Roll-On",
    category: "Medical & Pain Relief",
    price: 249,
    image_url: "https://images.unsplash.com/photo-1608571423902-eed4a5ad8108?auto=format&fit=crop&w=600&q=80",
    description: "Ayurvedic botanical cooling oil for fast abdominal pain ease"
  },
  {
    id: "d1111111-1111-1111-1111-111111111111",
    name: "CycleCare Dark Comfort Chocolate (70%)",
    category: "Comfort Treats",
    price: 120,
    image_url: "https://images.unsplash.com/photo-1549007994-cb92caebd54b?auto=format&fit=crop&w=600&q=80",
    description: "Rich dark chocolate with magnesium to ease muscle soreness"
  },
  {
    id: "carekit-premium-01",
    name: "CycleCare Emergency SOS Care Kit",
    category: "Emergency & Medical",
    price: 499,
    image_url: "https://images.unsplash.com/photo-1544367567-0f2fcb009e0b?auto=format&fit=crop&w=600&q=80",
    description: "Complete discreet kit with pads, heating patch, wipes & herbal tea"
  }
];

// Helper to clean display name (e.g. remove "(Husband)", "(Girl)")
function cleanName(rawName) {
  if (!rawName) return 'User';
  return rawName.replace(/\s*\((Husband|Girl|Partner|User|Male|Female)\)/gi, '').trim();
}

function mapToValidRelationship(tag) {
  if (!tag) return 'Other';
  const lower = tag.toLowerCase();
  if (lower.includes('husband')) return 'Husband';
  if (lower.includes('wife')) return 'Wife';
  if (lower.includes('best friend')) return 'Best Friend';
  if (lower.includes('sister')) return 'Sister';
  if (lower.includes('brother')) return 'Brother';
  if (lower.includes('mother') || lower.includes('mom')) return 'Mother';
  if (lower.includes('father') || lower.includes('dad')) return 'Father';
  if (lower.includes('boyfriend') || lower.includes('bf')) return 'Boyfriend';
  if (lower.includes('girlfriend') || lower.includes('gf')) return 'Girlfriend';
  if (lower.includes('partner')) return 'Partner';
  return 'Other';
}

const UUID_REGEX = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
const isValidUuid = (str) => typeof str === 'string' && UUID_REGEX.test(str.trim());

// 0. Curated Quick Care Items Getter
const getQuickCareItems = async (req, res, next) => {
  try {
    res.json({
      success: true,
      count: QUICK_CARE_ITEMS.length,
      items: QUICK_CARE_ITEMS
    });
  } catch (err) {
    next(err);
  }
};

// 1. Get Circle Contacts (Husband, Wife, Parents, Partner, Admin Help, etc.)
const getContacts = async (req, res, next) => {
  try {
    const userId = req.user.id;

    // 1. Fetch active partner connections for userId
    const { rows: connections } = await pool.query(
      `SELECT pc.id, pc.requester_id, pc.recipient_id, pc.relationship, pc.custom_relationship_label,
              pc.requester_relationship, pc.recipient_relationship, pc.requester_custom_label, pc.recipient_custom_label,
              pc.status, pc.created_at, pc.updated_at,
              u1.email as req_email, u1.cyclecare_id as req_cyclecare_id, p1.display_name as req_name,
              u2.email as rec_email, u2.cyclecare_id as rec_cyclecare_id, p2.display_name as rec_name
       FROM partner_connections pc
       LEFT JOIN users u1 ON u1.id = pc.requester_id
       LEFT JOIN profiles p1 ON p1.user_id = pc.requester_id
       LEFT JOIN users u2 ON u2.id = pc.recipient_id
       LEFT JOIN profiles p2 ON p2.user_id = pc.recipient_id
       WHERE (pc.requester_id = $1 OR pc.recipient_id = $1)
       ORDER BY pc.updated_at DESC`,
      [userId]
    );

    const contacts = [];
    const connectedUserIds = new Set();

    for (const c of connections) {
      const isRecipient = c.recipient_id === userId;
      const otherUserId = isRecipient ? c.requester_id : c.recipient_id;
      const otherEmail = isRecipient ? c.req_email : c.rec_email;
      const otherName = isRecipient ? c.req_name : c.rec_name;
      const otherCyclecareId = isRecipient ? c.req_cyclecare_id : c.rec_cyclecare_id;

      if (!otherUserId) continue;
      connectedUserIds.add(otherUserId);

      // Latest message
      const { rows: msgRows } = await pool.query(
        `SELECT content, message_type, created_at 
         FROM circle_messages 
         WHERE connection_id = $1 
         ORDER BY created_at DESC 
         LIMIT 1`,
        [c.id]
      );
      const latestMsg = msgRows.length > 0 ? msgRows[0] : null;

      // Unread count
      const { rows: unreadRows } = await pool.query(
        `SELECT COUNT(*)::int as unread 
         FROM circle_messages 
         WHERE connection_id = $1 AND receiver_id = $2 AND is_read = false`,
        [c.id, userId]
      );
      const unreadCount = unreadRows.length > 0 ? unreadRows[0].unread : 0;

      const rawDisplayName = otherName || (otherEmail ? otherEmail.split('@')[0] : 'Partner');
      const displayName = cleanName(rawDisplayName);
      const relationshipTag = resolveRelationshipForUser(c, userId);

      contacts.push({
        connection_id: c.id,
        user_id: otherUserId,
        display_name: displayName,
        cyclecare_id: otherCyclecareId ? `@${otherCyclecareId}` : `@${displayName.toLowerCase().replace(/\s+/g, '_')}`,
        relationship: relationshipTag,
        resolved_relationship: relationshipTag,
        last_message: latestMsg ? latestMsg.content : 'Start a caring conversation...',
        last_message_type: latestMsg ? latestMsg.message_type : 'TEXT',
        last_message_time: latestMsg ? latestMsg.created_at : c.created_at,
        unread_count: unreadCount
      });
    }

    // Ensure CycleCare Admin (Help) is auto-connected
    const { rows: adminRows } = await pool.query(
      `SELECT u.id, u.email, u.cyclecare_id, p.display_name 
       FROM users u 
       LEFT JOIN profiles p ON p.user_id = u.id 
       WHERE u.email = 'admin@cyclecare.app' 
       LIMIT 1`
    );

    if (adminRows.length > 0 && adminRows[0].id !== userId && !connectedUserIds.has(adminRows[0].id)) {
      const adminUser = adminRows[0];
      const { rows: newAdminConn } = await pool.query(
        `INSERT INTO partner_connections (requester_id, recipient_id, relationship, custom_relationship_label, status, created_at, updated_at)
         VALUES ($1, $2, 'Other', 'Admin (Help)', 'ACCEPTED', NOW(), NOW())
         RETURNING id, created_at`,
        [userId, adminUser.id]
      );
      if (newAdminConn.length > 0) {
        contacts.unshift({
          connection_id: newAdminConn[0].id,
          user_id: adminUser.id,
          display_name: 'CycleCare Admin (Help)',
          cyclecare_id: '@admin_help',
          relationship: 'Admin (Help)',
          last_message: 'Hello! Official CycleCare support is here for you. How can we help?',
          last_message_type: 'TEXT',
          last_message_time: newAdminConn[0].created_at,
          unread_count: 0
        });
        connectedUserIds.add(adminUser.id);
      }
    }

    // Ensure Aman Sharma (Husband) is auto-connected if not already
    const { rows: amanRows } = await pool.query(
      `SELECT u.id, u.email, u.cyclecare_id, p.display_name 
       FROM users u 
       LEFT JOIN profiles p ON p.user_id = u.id 
       WHERE u.email = 'aman.husband@cyclecare.app' 
       LIMIT 1`
    );

    if (amanRows.length > 0 && amanRows[0].id !== userId && !connectedUserIds.has(amanRows[0].id)) {
      const amanUser = amanRows[0];
      const { rows: newAmanConn } = await pool.query(
        `INSERT INTO partner_connections (requester_id, recipient_id, relationship, custom_relationship_label, status, created_at, updated_at)
         VALUES ($1, $2, 'Husband', 'Husband ❤️', 'ACCEPTED', NOW(), NOW())
         RETURNING id, created_at`,
        [userId, amanUser.id]
      );
      if (newAmanConn.length > 0) {
        contacts.push({
          connection_id: newAmanConn[0].id,
          user_id: amanUser.id,
          display_name: cleanName(amanUser.display_name || 'Aman Sharma'),
          cyclecare_id: '@aman_sharma',
          relationship: 'Husband ❤️',
          last_message: 'Hey, let me know if you need any pads, chocolates or medicines! ❤️',
          last_message_type: 'TEXT',
          last_message_time: newAmanConn[0].created_at,
          unread_count: 0
        });
        connectedUserIds.add(amanUser.id);
      }
    }

    // Include followed users
    const { rows: follows } = await pool.query(
      `SELECT uf.following_id, u.email, u.cyclecare_id, p.display_name 
       FROM user_follows uf
       JOIN users u ON u.id = uf.following_id
       LEFT JOIN profiles p ON p.user_id = u.id
       WHERE uf.follower_id = $1`,
      [userId]
    );

    for (const f of follows) {
      if (connectedUserIds.has(f.following_id)) continue;
      const { rows: newConn } = await pool.query(
        `INSERT INTO partner_connections (requester_id, recipient_id, relationship, custom_relationship_label, status, created_at, updated_at)
         VALUES ($1, $2, 'Other', 'Friend ✨', 'ACCEPTED', NOW(), NOW())
         RETURNING id, created_at`,
        [userId, f.following_id]
      );
      if (newConn.length > 0) {
        connectedUserIds.add(f.following_id);
        const name = cleanName(f.display_name || f.email.split('@')[0]);
        contacts.push({
          connection_id: newConn[0].id,
          user_id: f.following_id,
          display_name: name,
          cyclecare_id: f.cyclecare_id ? `@${f.cyclecare_id}` : `@${name.toLowerCase().replace(/\s+/g, '_')}`,
          relationship: 'Friend ✨',
          last_message: 'Connected on CycleCare! Say hello 🌸',
          last_message_type: 'TEXT',
          last_message_time: newConn[0].created_at,
          unread_count: 0
        });
      }
    }

    res.json({ success: true, count: contacts.length, contacts });
  } catch (err) {
    next(err);
  }
};

// 2. Get Messages for a Connection
const getMessages = async (req, res, next) => {
  try {
    const userId = req.user.id;
    let { connection_id } = req.params;

    if (!connection_id) {
      return res.status(400).json({ success: false, message: 'connection_id is required' });
    }

    // If demo connection id was passed by legacy client, resolve user's primary connection
    if (connection_id === 'demo-circle-connection') {
      const { rows: primaryRows } = await pool.query(
        `SELECT id FROM partner_connections 
         WHERE (requester_id = $1 OR recipient_id = $1) AND status = 'ACCEPTED'
         ORDER BY updated_at DESC LIMIT 1`,
        [userId]
      );
      if (primaryRows.length > 0) {
        connection_id = primaryRows[0].id;
      }
    }

    const { rows: messages } = await pool.query(
      `SELECT * FROM circle_messages 
       WHERE connection_id = $1 
       ORDER BY created_at ASC`,
      [connection_id]
    );

    // Mark received messages as read
    await pool.query(
      `UPDATE circle_messages 
       SET is_read = true 
       WHERE connection_id = $1 AND receiver_id = $2 AND is_read = false`,
      [connection_id, userId]
    );

    res.json({
      success: true,
      connection_id,
      messages: messages.map(m => ({
        ...m,
        is_mine: m.sender_id === userId
      }))
    });
  } catch (err) {
    next(err);
  }
};

// 3. Send Text Message
const sendMessage = async (req, res, next) => {
  try {
    const senderId = req.user.id;
    const { connection_id, receiver_id, content, message_type, metadata } = req.body;

    if (!content || !content.trim()) {
      return res.status(400).json({ success: false, message: 'Message content is required' });
    }

    let targetConnId = connection_id;
    let targetReceiverId = receiver_id;

    // Resolve connection & receiver if not provided or placeholder
    if (!targetConnId || targetConnId === 'demo-circle-connection') {
      if (targetReceiverId) {
        const { rows: cRows } = await pool.query(
          `SELECT id FROM partner_connections 
           WHERE (requester_id = $1 AND recipient_id = $2) OR (requester_id = $2 AND recipient_id = $1)`,
          [senderId, targetReceiverId]
        );
        if (cRows.length > 0) {
          targetConnId = cRows[0].id;
        } else {
          const { rows: nRows } = await pool.query(
            `INSERT INTO partner_connections (requester_id, recipient_id, relationship, custom_relationship_label, status, created_at, updated_at)
             VALUES ($1, $2, 'Other', 'Partner', 'ACCEPTED', NOW(), NOW())
             RETURNING id`,
            [senderId, targetReceiverId]
          );
          targetConnId = nRows[0].id;
        }
      } else {
        const { rows: pRows } = await pool.query(
          `SELECT id, requester_id, recipient_id FROM partner_connections 
           WHERE (requester_id = $1 OR recipient_id = $1) AND status = 'ACCEPTED'
           ORDER BY updated_at DESC LIMIT 1`,
          [senderId]
        );
        if (pRows.length > 0) {
          targetConnId = pRows[0].id;
          targetReceiverId = pRows[0].requester_id === senderId ? pRows[0].recipient_id : pRows[0].requester_id;
        }
      }
    } else if (!targetReceiverId) {
      const { rows: cRows } = await pool.query(
        `SELECT requester_id, recipient_id FROM partner_connections WHERE id = $1`,
        [targetConnId]
      );
      if (cRows.length > 0) {
        targetReceiverId = cRows[0].requester_id === senderId ? cRows[0].recipient_id : cRows[0].requester_id;
      }
    }

    if (!targetReceiverId) {
      // Find Aman or Admin
      const { rows: aRows } = await pool.query(
        `SELECT id FROM users WHERE email IN ('aman.husband@cyclecare.app', 'admin@cyclecare.app') AND id != $1 LIMIT 1`,
        [senderId]
      );
      if (aRows.length > 0) targetReceiverId = aRows[0].id;
    }

    const { rows: mRows } = await pool.query(
      `INSERT INTO circle_messages (connection_id, sender_id, receiver_id, message_type, content, metadata, is_read, created_at)
       VALUES ($1, $2, $3, $4, $5, $6, false, NOW())
       RETURNING *`,
      [targetConnId, senderId, targetReceiverId, message_type || 'TEXT', content.trim(), JSON.stringify(metadata || {})]
    );

    // Update partner_connections updated_at
    if (targetConnId) {
      await pool.query(`UPDATE partner_connections SET updated_at = NOW() WHERE id = $1`, [targetConnId]);
    }

    // Trigger FCM / Mobile push notification to recipient
    if (targetReceiverId) {
      (async () => {
        try {
          const { rows: senderRows } = await pool.query(
            `SELECT p.display_name, u.email FROM users u LEFT JOIN profiles p ON p.user_id = u.id WHERE u.id = $1`,
            [senderId]
          );
          const sName = (senderRows[0] && senderRows[0].display_name) || (senderRows[0] && senderRows[0].email ? senderRows[0].email.split('@')[0] : 'Partner');
          await sendChatPushNotification({
            senderId,
            senderName: sName,
            receiverId: targetReceiverId,
            messageText: content.trim(),
            connectionId: targetConnId,
            messageType: message_type || 'TEXT'
          });
        } catch (e) {
          console.error('Chat push notification dispatch error:', e.message);
        }
      })();
    }

    res.status(201).json({
      success: true,
      message: { ...mRows[0], is_mine: true }
    });
  } catch (err) {
    next(err);
  }
};

// 4. Send or Request a Care / Medical Item in Chat
const sendCareItem = async (req, res, next) => {
  try {
    const senderId = req.user.id;
    const { connection_id, receiver_id, item_name, item_price, item_category, item_image, is_request, note } = req.body;

    if (!item_name) {
      return res.status(400).json({ success: false, message: 'item_name is required' });
    }

    const messageType = is_request ? 'CARE_REQUEST' : 'CARE_ITEM_SENT';
    const content = note && note.trim().length > 0 
      ? note.trim() 
      : (is_request ? `Could you please arrange ${item_name}? 🌸` : `I sent you ${item_name} with love! ❤️`);

    const metadata = {
      item_name,
      item_price: Number(item_price) || 199,
      item_category: item_category || 'Care Essential',
      item_image: item_image || 'https://images.unsplash.com/photo-1544367567-0f2fcb009e0b?auto=format&fit=crop&w=600&q=80',
      status: is_request ? 'REQUESTED' : 'SENT'
    };

    let targetConnId = connection_id;
    let targetReceiverId = receiver_id;

    if (!targetConnId || targetConnId === 'demo-circle-connection') {
      if (targetReceiverId) {
        const { rows: cRows } = await pool.query(
          `SELECT id FROM partner_connections 
           WHERE (requester_id = $1 AND recipient_id = $2) OR (requester_id = $2 AND recipient_id = $1)`,
          [senderId, targetReceiverId]
        );
        if (cRows.length > 0) {
          targetConnId = cRows[0].id;
        } else {
          const { rows: nRows } = await pool.query(
            `INSERT INTO partner_connections (requester_id, recipient_id, relationship, custom_relationship_label, status, created_at, updated_at)
             VALUES ($1, $2, 'Other', 'Partner', 'ACCEPTED', NOW(), NOW())
             RETURNING id`,
            [senderId, targetReceiverId]
          );
          targetConnId = nRows[0].id;
        }
      } else {
        const { rows: pRows } = await pool.query(
          `SELECT id, requester_id, recipient_id FROM partner_connections 
           WHERE (requester_id = $1 OR recipient_id = $1) AND status = 'ACCEPTED'
           ORDER BY updated_at DESC LIMIT 1`,
          [senderId]
        );
        if (pRows.length > 0) {
          targetConnId = pRows[0].id;
          targetReceiverId = pRows[0].requester_id === senderId ? pRows[0].recipient_id : pRows[0].requester_id;
        }
      }
    } else if (!targetReceiverId) {
      const { rows: cRows } = await pool.query(
        `SELECT requester_id, recipient_id FROM partner_connections WHERE id = $1`,
        [targetConnId]
      );
      if (cRows.length > 0) {
        targetReceiverId = cRows[0].requester_id === senderId ? cRows[0].recipient_id : cRows[0].requester_id;
      }
    }

    if (!targetReceiverId) {
      const { rows: aRows } = await pool.query(
        `SELECT id FROM users WHERE email IN ('aman.husband@cyclecare.app', 'admin@cyclecare.app') AND id != $1 LIMIT 1`,
        [senderId]
      );
      if (aRows.length > 0) targetReceiverId = aRows[0].id;
    }

    const { rows: mRows } = await pool.query(
      `INSERT INTO circle_messages (connection_id, sender_id, receiver_id, message_type, content, metadata, is_read, created_at)
       VALUES ($1, $2, $3, $4, $5, $6, false, NOW())
       RETURNING *`,
      [targetConnId, senderId, targetReceiverId, messageType, content, JSON.stringify(metadata)]
    );

    if (targetConnId) {
      await pool.query(`UPDATE partner_connections SET updated_at = NOW() WHERE id = $1`, [targetConnId]);
    }

    // Trigger FCM / Mobile push notification to recipient
    if (targetReceiverId) {
      (async () => {
        try {
          const { rows: senderRows } = await pool.query(
            `SELECT p.display_name, u.email FROM users u LEFT JOIN profiles p ON p.user_id = u.id WHERE u.id = $1`,
            [senderId]
          );
          const sName = (senderRows[0] && senderRows[0].display_name) || (senderRows[0] && senderRows[0].email ? senderRows[0].email.split('@')[0] : 'Partner');
          await sendChatPushNotification({
            senderId,
            senderName: sName,
            receiverId: targetReceiverId,
            messageText: content,
            connectionId: targetConnId,
            messageType: messageType
          });
        } catch (e) {
          console.error('Care item push notification dispatch error:', e.message);
        }
      })();
    }

    res.status(201).json({
      success: true,
      message: { ...mRows[0], is_mine: true }
    });
  } catch (err) {
    next(err);
  }
};

// 5. Set custom relationship tag for a contact (Bidirectional Reciprocal Persistence)
const setContactTag = async (req, res, next) => {
  try {
    const userId = req.user.id;
    const { connection_id, target_user_id, target_name, tag, reciprocal_relationship } = req.body;

    if (!tag || !tag.trim()) {
      return res.status(400).json({ success: false, message: 'tag is required' });
    }

    const cleanTag = tag.trim();

    // 1. Resolve target connection and target user ID
    let conn = null;
    let targetUserId = (target_user_id && isValidUuid(target_user_id)) ? target_user_id : null;

    if (connection_id && isValidUuid(connection_id)) {
      const { rows } = await pool.query(
        `SELECT * FROM partner_connections 
         WHERE id = $1 AND (requester_id = $2 OR recipient_id = $2)`,
        [connection_id, userId]
      );
      if (rows.length > 0) {
        conn = rows[0];
        targetUserId = conn.requester_id === userId ? conn.recipient_id : conn.requester_id;
      }
    }

    if (!conn && targetUserId) {
      const { rows } = await pool.query(
        `SELECT * FROM partner_connections 
         WHERE (requester_id = $1 AND recipient_id = $2) OR (requester_id = $2 AND recipient_id = $1)`,
        [userId, targetUserId]
      );
      if (rows.length > 0) {
        conn = rows[0];
      }
    }

    if (!conn && !targetUserId && target_name && target_name.trim().length > 0) {
      const cleanTargetName = cleanName(target_name.trim());
      const { rows: matchedUsers } = await pool.query(
        `SELECT u.id FROM users u
         LEFT JOIN profiles p ON p.user_id = u.id
         WHERE (p.display_name ILIKE $1 OR u.email ILIKE $1) AND u.id != $2
         LIMIT 1`,
        [`%${cleanTargetName}%`, userId]
      );
      if (matchedUsers.length > 0) {
        targetUserId = matchedUsers[0].id;
        const { rows } = await pool.query(
          `SELECT * FROM partner_connections 
           WHERE (requester_id = $1 AND recipient_id = $2) OR (requester_id = $2 AND recipient_id = $1)`,
          [userId, targetUserId]
        );
        if (rows.length > 0) {
          conn = rows[0];
        }
      }
    }

    // If still no target user found
    if (!conn && !targetUserId) {
      return res.status(404).json({ success: false, message: 'Target user or connection not found' });
    }

    // If no existing connection, create one
    if (!conn && targetUserId) {
      const { rows: newConn } = await pool.query(
        `INSERT INTO partner_connections 
         (requester_id, recipient_id, status, relationship, requester_relationship, recipient_relationship, created_at, updated_at)
         VALUES ($1, $2, 'ACCEPTED', 'Partner', 'Partner', 'Partner', NOW(), NOW())
         RETURNING *`,
        [userId, targetUserId]
      );
      conn = newConn[0];
    }

    if (!targetUserId) {
      targetUserId = conn.requester_id === userId ? conn.recipient_id : conn.requester_id;
    }

    // 2. Fetch Demographics for Actor and Target
    const actorDemo = await getUserDemographics(userId);
    const targetDemo = await getUserDemographics(targetUserId);

    // 3. Determine Reciprocal Mapping
    let mapping;
    try {
      mapping = determineReciprocal({
        assignedTag: cleanTag,
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

    const assignedTag = mapping.assigned;
    const reciprocalTag = mapping.reciprocal;
    const isRequester = conn.requester_id === userId;

    // 4. Update partner_connections atomically
    if (isRequester) {
      await pool.query(
        `UPDATE partner_connections 
         SET requester_relationship = $1, recipient_relationship = $2,
             requester_custom_label = $3,
             relationship = $1, custom_relationship_label = $3,
             updated_at = NOW() 
         WHERE id = $4`,
        [assignedTag, reciprocalTag, cleanTag, conn.id]
      );
    } else {
      await pool.query(
        `UPDATE partner_connections 
         SET recipient_relationship = $1, requester_relationship = $2,
             recipient_custom_label = $3,
             relationship = $2, custom_relationship_label = $3,
             updated_at = NOW() 
         WHERE id = $4`,
        [assignedTag, reciprocalTag, cleanTag, conn.id]
      );
    }

    // 5. Audit Trail
    try {
      await pool.query(
        `INSERT INTO sharing_audit_events (connection_id, actor_id, event_type, target_user_id, metadata)
         VALUES ($1, $2, 'RELATIONSHIP_UPDATED', $3, $4)`,
        [conn.id, userId, targetUserId, JSON.stringify({
          assigned: assignedTag,
          reciprocal: reciprocalTag,
          source: 'CHAT'
        })]
      );
    } catch (_) {}

    // Update account_tag in profiles table for quick glance
    if (targetUserId) {
      try {
        await pool.query(
          `UPDATE profiles SET account_tag = $1, updated_at = NOW() WHERE user_id = $2`,
          [assignedTag, targetUserId]
        );
      } catch (_) {}
    }

    res.json({
      success: true,
      connection_id: conn.id,
      target_user_id: targetUserId,
      tag: assignedTag,
      relationship: assignedTag,
      reciprocal_relationship: reciprocalTag,
      message: `Relationship updated to "${assignedTag}" (reciprocal: "${reciprocalTag}")`
    });
  } catch (err) {
    next(err);
  }
};

// 6. Search Users by name or email
const searchUsers = async (req, res, next) => {
  try {
    const { query } = req.query;
    const currentUserId = req.user.id;

    if (!query || query.trim().length === 0) {
      return res.json({ success: true, users: [] });
    }

    const cleanQ = query.trim();

    // Query users & profiles from PostgreSQL
    const { rows: matchedUsers } = await pool.query(
      `SELECT u.id, u.email, u.role, p.display_name, p.profile_image
       FROM users u
       LEFT JOIN profiles p ON p.user_id = u.id
       WHERE u.id != $1 AND (u.email ILIKE $2 OR p.display_name ILIKE $2)
       LIMIT 20`,
      [currentUserId, `%${cleanQ}%`]
    );

    // Query following status
    let followingSet = new Set();
    try {
      const { rows: follows } = await pool.query(
        `SELECT following_id FROM user_follows WHERE follower_id = $1`,
        [currentUserId]
      );
      followingSet = new Set(follows.map(f => f.following_id));
    } catch (_) {}

    const mapped = matchedUsers.map(u => ({
      id: u.id,
      email: u.email,
      display_name: cleanName(u.display_name || u.email.split('@')[0]),
      profile_image: u.profile_image || null,
      is_following: followingSet.has(u.id)
    }));

    res.json({ success: true, count: mapped.length, users: mapped });
  } catch (err) {
    next(err);
  }
};

// 7. Follow User
const followUser = async (req, res, next) => {
  try {
    const followerId = req.user.id;
    const { target_user_id } = req.body;

    if (!target_user_id) {
      return res.status(400).json({ success: false, message: 'target_user_id required' });
    }
    if (followerId === target_user_id) {
      return res.status(400).json({ success: false, message: 'Cannot follow yourself' });
    }

    await pool.query(
      `INSERT INTO user_follows (follower_id, following_id, created_at)
       VALUES ($1, $2, NOW())
       ON CONFLICT (follower_id, following_id) DO NOTHING`,
      [followerId, target_user_id]
    );

    res.json({ success: true, message: 'User followed successfully', is_following: true });
  } catch (err) {
    next(err);
  }
};

// 8. Unfollow User
const unfollowUser = async (req, res, next) => {
  try {
    const followerId = req.user.id;
    const { target_user_id } = req.body;

    if (!target_user_id) {
      return res.status(400).json({ success: false, message: 'target_user_id required' });
    }

    await pool.query(
      `DELETE FROM user_follows WHERE follower_id = $1 AND following_id = $2`,
      [followerId, target_user_id]
    );

    res.json({ success: true, message: 'User unfollowed successfully', is_following: false });
  } catch (err) {
    next(err);
  }
};

// 9. Get User Social Stats (Followers / Following counts)
const getUserSocialStats = async (req, res, next) => {
  try {
    const targetUserId = req.params.userId || req.user.id;

    const { rows: fRows } = await pool.query(
      `SELECT COUNT(*)::int as count FROM user_follows WHERE following_id = $1`,
      [targetUserId]
    );
    const { rows: fgRows } = await pool.query(
      `SELECT COUNT(*)::int as count FROM user_follows WHERE follower_id = $1`,
      [targetUserId]
    );

    res.json({
      success: true,
      stats: {
        followers: fRows.length > 0 ? fRows[0].count : 0,
        following: fgRows.length > 0 ? fgRows[0].count : 0
      }
    });
  } catch (err) {
    next(err);
  }
};

// 10. Get Followers List
const getFollowers = async (req, res, next) => {
  try {
    const targetUserId = req.params.userId || req.user.id;
    const currentUserId = req.user.id;

    const { rows } = await pool.query(
      `SELECT uf.follower_id, uf.created_at, u.email, u.cyclecare_id, p.display_name, p.profile_image
       FROM user_follows uf
       JOIN users u ON u.id = uf.follower_id
       LEFT JOIN profiles p ON p.user_id = u.id
       WHERE uf.following_id = $1
       ORDER BY uf.created_at DESC`,
      [targetUserId]
    );

    const followerIds = rows.map(r => r.follower_id);
    let myFollowings = new Set();
    if (followerIds.length > 0) {
      const { rows: myF } = await pool.query(
        `SELECT following_id FROM user_follows WHERE follower_id = $1 AND following_id = ANY($2::uuid[])`,
        [currentUserId, followerIds]
      );
      myFollowings = new Set(myF.map(f => f.following_id));
    }

    const followers = rows.map(r => {
      const name = cleanName(r.display_name || r.email.split('@')[0]);
      return {
        id: r.follower_id,
        display_name: name,
        email: r.email,
        avatar_url: r.profile_image || null,
        is_following: myFollowings.has(r.follower_id),
        is_me: r.follower_id === currentUserId,
        followed_at: r.created_at
      };
    });

    res.json({ success: true, count: followers.length, users: followers });
  } catch (err) {
    next(err);
  }
};

// 11. Get Following List
const getFollowing = async (req, res, next) => {
  try {
    const targetUserId = req.params.userId || req.user.id;
    const currentUserId = req.user.id;

    const { rows } = await pool.query(
      `SELECT uf.following_id, uf.created_at, u.email, u.cyclecare_id, p.display_name, p.profile_image
       FROM user_follows uf
       JOIN users u ON u.id = uf.following_id
       LEFT JOIN profiles p ON p.user_id = u.id
       WHERE uf.follower_id = $1
       ORDER BY uf.created_at DESC`,
      [targetUserId]
    );

    const following = rows.map(r => {
      const name = cleanName(r.display_name || r.email.split('@')[0]);
      return {
        id: r.following_id,
        display_name: name,
        email: r.email,
        avatar_url: r.profile_image || null,
        is_following: true,
        is_me: r.following_id === currentUserId,
        followed_at: r.created_at
      };
    });

    res.json({ success: true, count: following.length, users: following });
  } catch (err) {
    next(err);
  }
};

// 12. Delete Message
const deleteMessage = async (req, res, next) => {
  try {
    const userId = req.user.id;
    const { messageId } = req.params;

    if (!messageId) {
      return res.status(400).json({ success: false, message: 'messageId is required' });
    }

    const { rows: msgRows } = await pool.query(
      `SELECT * FROM circle_messages WHERE id = $1`,
      [messageId]
    );

    if (msgRows.length === 0) {
      return res.status(404).json({ success: false, message: 'Message not found' });
    }

    const msg = msgRows[0];
    if (msg.sender_id !== userId && req.user.role !== 'ADMIN') {
      return res.status(403).json({ success: false, message: 'Permission denied: You can only delete your own messages' });
    }

    await pool.query(`DELETE FROM circle_messages WHERE id = $1`, [messageId]);

    res.json({ success: true, message: 'Message deleted successfully', message_id: messageId });
  } catch (err) {
    next(err);
  }
};

// 13. Delete Contact & Entire Conversation
const deleteContact = async (req, res, next) => {
  try {
    const userId = req.user.id;
    const { connection_id } = req.params;

    if (!connection_id) {
      return res.status(400).json({ success: false, message: 'connection_id is required' });
    }

    await pool.query(`DELETE FROM circle_messages WHERE connection_id = $1`, [connection_id]);
    await pool.query(
      `DELETE FROM partner_connections WHERE id = $1 AND (requester_id = $2 OR recipient_id = $2)`,
      [connection_id, userId]
    );

    res.json({ success: true, message: 'Contact and conversation deleted' });
  } catch (err) {
    next(err);
  }
};

module.exports = {
  getContacts,
  getMessages,
  sendMessage,
  sendCareItem,
  getQuickCareItems,
  searchUsers,
  followUser,
  unfollowUser,
  getUserSocialStats,
  getFollowers,
  getFollowing,
  setContactTag,
  deleteMessage,
  deleteContact
};
