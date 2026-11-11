const pool = require('../config/db');

const demoEmails = [
  'admin@cyclecare.app',
  'demo@cyclecare.com',
  'husband.demo@cyclecare.app',
  'delivery.demo@cyclecare.app',
  'newuser@cyclecare.com',
  'aman.husband@cyclecare.app'
];

function isDemoEmail(email) {
  if (!email) return false;
  const lower = email.toLowerCase().trim();
  return (
    demoEmails.includes(lower) ||
    lower.includes('demo') ||
    lower.endsWith('@cyclecare.app') ||
    lower.endsWith('@cyclecare.com')
  );
}

const getDashboardStats = async (req, res, next) => {
  try {
    const userCountRes = await pool.query('SELECT count(*)::int AS count FROM users');
    const totalUsers = userCountRes.rows[0].count;

    const allUsersRes = await pool.query('SELECT email FROM users');
    let demoCount = 0;
    let realCount = 0;
    allUsersRes.rows.forEach(u => {
      if (isDemoEmail(u.email)) {
        demoCount++;
      } else {
        realCount++;
      }
    });

    const ordersCountRes = await pool.query('SELECT count(*)::int AS count FROM orders');
    const totalOrders = ordersCountRes.rows[0].count;

    const revenueRes = await pool.query(
      "SELECT COALESCE(SUM(total_amount), 0)::numeric AS revenue FROM orders WHERE status IN ('PAID', 'COMPLETED', 'DELIVERED') OR payment_status = 'PAID'"
    );
    const totalRevenue = parseFloat(revenueRes.rows[0].revenue || 0);

    const productsRes = await pool.query('SELECT count(*)::int AS total, count(*) FILTER (WHERE status = \'PUBLISHED\' OR (status IS NULL AND is_active = true))::int AS live, count(*) FILTER (WHERE status = \'DRAFT\')::int AS drafts, count(*) FILTER (WHERE stock <= 5)::int AS low_stock FROM products');
    const productStats = productsRes.rows[0];

    const lowStockListRes = await pool.query(
      'SELECT id, name, sku, stock, price, discount_price FROM products WHERE stock <= 5 ORDER BY stock ASC LIMIT 10'
    );

    const partnerRes = await pool.query(
      "SELECT count(*)::int AS total, count(*) FILTER (WHERE status = 'ACCEPTED')::int AS active, count(*) FILTER (WHERE status = 'PENDING')::int AS pending FROM partner_connections"
    );
    const partnerStats = partnerRes.rows[0];

    const chatCountRes = await pool.query('SELECT count(*)::int AS count FROM circle_messages');
    const totalCircleMessages = chatCountRes.rows[0].count;

    res.json({
      success: true,
      stats: {
        totalUsers,
        realUsersCount: realCount,
        demoUsersCount: demoCount,
        totalOrders,
        totalRevenue,
        totalProducts: productStats.total,
        liveProductsCount: productStats.live,
        draftProductsCount: productStats.drafts,
        lowStockAlertsCount: productStats.low_stock,
        totalCircleMessages,
        partnerConnections: {
          total: partnerStats.total,
          active: partnerStats.active,
          pending: partnerStats.pending
        }
      },
      lowStockProducts: lowStockListRes.rows
    });
  } catch (err) {
    next(err);
  }
};

const getUsers = async (req, res, next) => {
  try {
    const sql = `
      SELECT 
        u.id, 
        u.email, 
        u.role, 
        u.status, 
        u.usage_mode, 
        u.gender, 
        u.created_at, 
        u.updated_at,
        p.display_name, 
        p.account_tag, 
        p.emergency_contact_phone, 
        p.emergency_contact_name, 
        p.emergency_contact_relation
      FROM users u
      LEFT JOIN profiles p ON u.id = p.user_id
      ORDER BY u.created_at DESC
    `;
    const result = await pool.query(sql);

    const users = result.rows.map(u => {
      const isDemo = isDemoEmail(u.email);
      let accountTag = u.account_tag;
      if (!accountTag) {
        if (u.email === 'admin@cyclecare.app') accountTag = 'DEMO ADMIN';
        else if (u.email === 'demo@cyclecare.com') accountTag = 'DEMO GIRL';
        else if (u.email === 'husband.demo@cyclecare.app') accountTag = 'DEMO HUSBAND';
        else if (u.email === 'aman.husband@cyclecare.app') accountTag = 'DEMO HUSBAND (AMAN)';
        else if (u.email === 'delivery.demo@cyclecare.app') accountTag = 'DEMO COURIER';
        else if (isDemo) accountTag = 'DEMO USER';
        else accountTag = 'ORGANIC REAL USER';
      }

      const displayName = u.display_name || (u.email ? u.email.split('@')[0] : 'User');

      return {
        id: u.id,
        email: u.email,
        role: u.role || 'USER',
        status: u.status || 'ACTIVE',
        usage_mode: u.usage_mode || 'TRACK_CYCLE',
        gender: u.gender || 'FEMALE',
        created_at: u.created_at,
        account_type: isDemo ? 'DEMO' : 'REAL',
        account_tag: accountTag,
        display_name: displayName,
        profiles: {
          display_name: displayName,
          account_tag: accountTag,
          emergency_contact_phone: u.emergency_contact_phone,
          emergency_contact_name: u.emergency_contact_name,
          emergency_contact_relation: u.emergency_contact_relation
        }
      };
    });

    res.json({ success: true, count: users.length, users });
  } catch (err) {
    next(err);
  }
};

const updateUserTag = async (req, res, next) => {
  try {
    const userId = req.params.id;
    const { account_tag, tag, display_name, role, status } = req.body;
    const finalTag = account_tag !== undefined ? account_tag : tag;

    // Check if profile exists
    const profCheck = await pool.query('SELECT id FROM profiles WHERE user_id = $1', [userId]);
    if (profCheck.rows.length > 0) {
      const updates = [];
      const vals = [userId];
      if (finalTag !== undefined) {
        vals.push(finalTag.trim());
        updates.push(`account_tag = $${vals.length}`);
      }
      if (display_name !== undefined) {
        vals.push(display_name.trim());
        updates.push(`display_name = $${vals.length}`);
      }
      if (updates.length > 0) {
        updates.push('updated_at = NOW()');
        await pool.query(`UPDATE profiles SET ${updates.join(', ')} WHERE user_id = $1`, vals);
      }
    } else {
      await pool.query(
        'INSERT INTO profiles (user_id, account_tag, display_name, updated_at) VALUES ($1, $2, $3, NOW())',
        [userId, (finalTag || '').trim(), (display_name || '').trim()]
      );
    }

    if (role || status) {
      const uUpdates = [];
      const uVals = [userId];
      if (role) {
        uVals.push(role);
        uUpdates.push(`role = $${uVals.length}`);
      }
      if (status) {
        uVals.push(status);
        uUpdates.push(`status = $${uVals.length}`);
      }
      if (uUpdates.length > 0) {
        uUpdates.push('updated_at = NOW()');
        await pool.query(`UPDATE users SET ${uUpdates.join(', ')} WHERE id = $1`, uVals);
      }
    }

    res.json({ success: true, message: 'User tag and details updated successfully' });
  } catch (err) {
    next(err);
  }
};

const getUserCycleLogs = async (req, res, next) => {
  try {
    const userId = req.params.id;
    const periodRes = await pool.query(
      'SELECT id, user_id, start_date, end_date, flow, notes FROM period_logs WHERE user_id = $1 ORDER BY start_date DESC',
      [userId]
    );

    const symptomRes = await pool.query(
      'SELECT sl.id, sl.user_id, sl.log_date, sl.intensity, sl.notes, s.name AS symptom_name FROM symptom_logs sl LEFT JOIN symptoms s ON sl.symptom_id = s.id WHERE sl.user_id = $1 ORDER BY sl.log_date DESC LIMIT 20',
      [userId]
    );

    const moodRes = await pool.query(
      'SELECT ml.id, ml.user_id, ml.log_date, ml.intensity, ml.notes, m.name AS mood_name FROM mood_logs ml LEFT JOIN moods m ON ml.mood_id = m.id WHERE ml.user_id = $1 ORDER BY ml.log_date DESC LIMIT 20',
      [userId]
    );

    res.json({
      success: true,
      period_logs: periodRes.rows || [],
      symptoms: symptomRes.rows || [],
      moods: moodRes.rows || []
    });
  } catch (err) {
    next(err);
  }
};

const updateUserStatus = async (req, res, next) => {
  try {
    const userId = req.params.id;
    const { status } = req.body;

    if (!['ACTIVE', 'DISABLED', 'SUSPENDED'].includes(status)) {
      return res.status(400).json({ success: false, message: 'Invalid status' });
    }

    const resUpdate = await pool.query('UPDATE users SET status = $1, updated_at = NOW() WHERE id = $2 RETURNING *', [status, userId]);
    if (resUpdate.rows.length === 0) return res.status(404).json({ success: false, message: 'User not found' });

    res.json({ success: true, message: 'User status updated', user: resUpdate.rows[0] });
  } catch (err) {
    next(err);
  }
};

const getAdminProducts = async (req, res, next) => {
  try {
    const sql = `
      SELECT 
        p.*, 
        c.name AS category_name 
      FROM products p 
      LEFT JOIN categories c ON p.category_id = c.id 
      ORDER BY p.created_at DESC
    `;
    const result = await pool.query(sql);

    const products = result.rows.map(p => ({
      ...p,
      categories: { name: p.category_name || 'General Care' }
    }));

    res.json({ success: true, count: products.length, products });
  } catch (err) {
    next(err);
  }
};

const createProduct = async (req, res, next) => {
  try {
    const { category_id, name, brand, description, price, discount_price, stock, sku, status, images } = req.body;

    if (!name || price === undefined || !sku) {
      return res.status(400).json({ success: false, message: 'Name, price, and SKU are required' });
    }

    const productStatus = status || 'DRAFT';
    const numPrice = parseFloat(price);
    const numDiscount = discount_price ? parseFloat(discount_price) : null;
    const numStock = stock ? parseInt(stock) : 0;
    const imgUrl = (images && images.length > 0) ? images[0] : null;

    const sql = `
      INSERT INTO products (
        category_id, name, brand, description, price, discount_price, stock, sku, status, is_active, image_url, created_at, updated_at
      ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, true, $10, NOW(), NOW())
      RETURNING *
    `;
    const insRes = await pool.query(sql, [
      category_id || '11111111-1111-1111-1111-111111111111',
      name.trim(),
      brand ? brand.trim() : 'CycleCare',
      description ? description.trim() : '',
      numPrice,
      numDiscount,
      numStock,
      sku.trim(),
      productStatus,
      imgUrl
    ]);

    const product = insRes.rows[0];

    if (imgUrl) {
      await pool.query(
        'INSERT INTO product_images (product_id, image_url, sort_order, is_main, is_thumbnail) VALUES ($1, $2, 0, true, true)',
        [product.id, imgUrl]
      );
    }

    // Inventory movement
    await pool.query(
      'INSERT INTO inventory_movements (product_id, movement_type, quantity, previous_stock, new_stock, reason, created_at) VALUES ($1, $2, $3, $4, $5, $6, NOW())',
      [product.id, 'ADD', numStock, 0, numStock, 'Initial Product Stock']
    );

    res.status(201).json({ success: true, message: 'Product created successfully', product });
  } catch (err) {
    next(err);
  }
};

const updateProduct = async (req, res, next) => {
  try {
    const productId = req.params.id;
    const { category_id, name, brand, description, price, discount_price, stock, sku, status, is_active, images } = req.body;

    const existRes = await pool.query('SELECT * FROM products WHERE id = $1', [productId]);
    if (existRes.rows.length === 0) return res.status(404).json({ success: false, message: 'Product not found' });
    const existing = existRes.rows[0];

    const updates = [];
    const vals = [productId];

    if (name !== undefined) { vals.push(name.trim()); updates.push(`name = $${vals.length}`); }
    if (brand !== undefined) { vals.push(brand.trim()); updates.push(`brand = $${vals.length}`); }
    if (description !== undefined) { vals.push(description.trim()); updates.push(`description = $${vals.length}`); }
    if (category_id !== undefined) { vals.push(category_id); updates.push(`category_id = $${vals.length}`); }
    if (price !== undefined) { vals.push(parseFloat(price)); updates.push(`price = $${vals.length}`); }
    if (discount_price !== undefined) { vals.push(discount_price ? parseFloat(discount_price) : null); updates.push(`discount_price = $${vals.length}`); }
    if (sku !== undefined) { vals.push(sku.trim()); updates.push(`sku = $${vals.length}`); }
    if (status !== undefined) { vals.push(status); updates.push(`status = $${vals.length}`); }
    if (is_active !== undefined) { vals.push(is_active); updates.push(`is_active = $${vals.length}`); }

    if (stock !== undefined && parseInt(stock) !== existing.stock) {
      const newStock = parseInt(stock);
      const diff = newStock - existing.stock;
      vals.push(newStock);
      updates.push(`stock = $${vals.length}`);

      await pool.query(
        'INSERT INTO inventory_movements (product_id, movement_type, quantity, previous_stock, new_stock, reason, created_at) VALUES ($1, $2, $3, $4, $5, $6, NOW())',
        [productId, diff > 0 ? 'ADD' : 'REMOVE', Math.abs(diff), existing.stock, newStock, 'Admin Manual Adjustment']
      );
    }

    if (images && images.length > 0) {
      vals.push(images[0]);
      updates.push(`image_url = $${vals.length}`);
    }

    updates.push('updated_at = NOW()');

    const updateSql = `UPDATE products SET ${updates.join(', ')} WHERE id = $1 RETURNING *`;
    const resUpdate = await pool.query(updateSql, vals);

    res.json({ success: true, message: 'Product updated', product: resUpdate.rows[0] });
  } catch (err) {
    next(err);
  }
};

const deleteProduct = async (req, res, next) => {
  try {
    const productId = req.params.id;
    await pool.query('DELETE FROM product_images WHERE product_id = $1', [productId]);
    await pool.query('DELETE FROM inventory_movements WHERE product_id = $1', [productId]);
    await pool.query('DELETE FROM products WHERE id = $1', [productId]);
    res.json({ success: true, message: 'Product deleted successfully' });
  } catch (err) {
    next(err);
  }
};

const getAdminOrders = async (req, res, next) => {
  try {
    const sql = `
      SELECT 
        o.*,
        u.email AS user_email,
        a.address_line,
        a.city,
        a.state,
        a.pincode,
        a.phone AS address_phone
      FROM orders o
      LEFT JOIN users u ON o.user_id = u.id
      LEFT JOIN addresses a ON o.address_id = a.id
      ORDER BY o.created_at DESC
    `;
    const ordersRes = await pool.query(sql);

    const itemsRes = await pool.query(`
      SELECT oi.*, p.name AS product_name 
      FROM order_items oi 
      LEFT JOIN products p ON oi.product_id = p.id
    `);

    const itemsByOrder = {};
    itemsRes.rows.forEach(item => {
      if (!itemsByOrder[item.order_id]) itemsByOrder[item.order_id] = [];
      itemsByOrder[item.order_id].push(item);
    });

    const orders = ordersRes.rows.map(o => {
      const isDemo = isDemoEmail(o.user_email) || (o.order_number && o.order_number.includes('DEMO'));
      return {
        ...o,
        order_type: isDemo ? 'DEMO' : 'REAL',
        order_items: itemsByOrder[o.id] || [],
        users: { email: o.user_email },
        addresses: {
          address_line: o.address_line,
          city: o.city,
          state: o.state,
          pincode: o.pincode,
          phone: o.address_phone
        }
      };
    });

    res.json({ success: true, count: orders.length, orders });
  } catch (err) {
    next(err);
  }
};

const updateOrderStatus = async (req, res, next) => {
  try {
    const orderId = req.params.id;
    const { status, delivery_status, payment_status } = req.body;

    const updates = [];
    const vals = [orderId];

    if (status) { vals.push(status); updates.push(`status = $${vals.length}`); }
    if (delivery_status) { vals.push(delivery_status); updates.push(`delivery_status = $${vals.length}`); }
    if (payment_status) { vals.push(payment_status); updates.push(`payment_status = $${vals.length}`); }

    if (updates.length === 0) return res.status(400).json({ success: false, message: 'No fields to update' });

    updates.push('updated_at = NOW()');
    const resUpdate = await pool.query(`UPDATE orders SET ${updates.join(', ')} WHERE id = $1 RETURNING *`, vals);
    if (resUpdate.rows.length === 0) return res.status(404).json({ success: false, message: 'Order not found' });

    res.json({ success: true, message: 'Order status updated', order: resUpdate.rows[0] });
  } catch (err) {
    next(err);
  }
};

const getAdminDeliveries = async (req, res, next) => {
  try {
    const sql = `
      SELECT 
        d.*,
        o.order_number,
        o.total_amount,
        o.delivery_status AS order_delivery_status,
        o.delivery_otp AS order_otp,
        a.address_line,
        a.city,
        da.name AS agent_name,
        da.phone AS agent_phone,
        da.is_demo AS agent_is_demo
      FROM deliveries d
      LEFT JOIN orders o ON d.order_id = o.id
      LEFT JOIN addresses a ON o.address_id = a.id
      LEFT JOIN delivery_agents da ON d.agent_id = da.id
      ORDER BY d.created_at DESC
    `;
    const result = await pool.query(sql);

    const deliveries = result.rows.map(d => ({
      id: d.id,
      order_id: d.order_id,
      agent_id: d.agent_id,
      status: d.status,
      delivery_otp: d.delivery_otp || d.order_otp || '4821',
      pickup_time: d.pickup_time,
      accepted_at: d.accepted_at,
      picked_up_at: d.picked_up_at,
      started_at: d.started_at,
      arrived_at: d.arrived_at,
      delivered_at: d.delivered_at,
      created_at: d.created_at,
      orders: {
        order_number: d.order_number || '#CC-DEMO-1001',
        total_amount: d.total_amount,
        delivery_address: d.address_line ? `${d.address_line}, ${d.city}` : 'Demo Care Address, Green Avenue'
      },
      delivery_agents: {
        name: d.agent_name || 'CycleCare Courier',
        phone: d.agent_phone || '+91 9876543210',
        is_demo: d.agent_is_demo !== false
      }
    }));

    res.json({ success: true, count: deliveries.length, deliveries });
  } catch (err) {
    next(err);
  }
};

const getChatLogs = async (req, res, next) => {
  try {
    const sql = `
      SELECT 
        cm.id,
        cm.connection_id,
        cm.sender_id,
        cm.receiver_id,
        cm.message_type,
        cm.content,
        cm.metadata,
        cm.is_read,
        cm.created_at,
        su.email AS sender_email,
        sp.display_name AS sender_name,
        ru.email AS receiver_email,
        rp.display_name AS receiver_name
      FROM circle_messages cm
      LEFT JOIN users su ON cm.sender_id = su.id
      LEFT JOIN profiles sp ON su.id = sp.user_id
      LEFT JOIN users ru ON cm.receiver_id = ru.id
      LEFT JOIN profiles rp ON ru.id = rp.user_id
      ORDER BY cm.created_at DESC
      LIMIT 100
    `;
    const result = await pool.query(sql);

    const messages = result.rows.map(m => {
      const senderIsDemo = isDemoEmail(m.sender_email);
      const receiverIsDemo = isDemoEmail(m.receiver_email);
      const isDemo = senderIsDemo || receiverIsDemo;

      return {
        id: m.id,
        connection_id: m.connection_id,
        sender_id: m.sender_id,
        receiver_id: m.receiver_id,
        sender_name: m.sender_name || (m.sender_email ? m.sender_email.split('@')[0] : 'Sender'),
        receiver_name: m.receiver_name || (m.receiver_email ? m.receiver_email.split('@')[0] : 'Receiver'),
        sender_email: m.sender_email,
        receiver_email: m.receiver_email,
        message_type: m.message_type || 'TEXT',
        content: m.content,
        metadata: m.metadata || {},
        is_read: m.is_read,
        is_demo: isDemo,
        created_at: m.created_at
      };
    });

    res.json({ success: true, count: messages.length, messages });
  } catch (err) {
    next(err);
  }
};

const getAuditLogs = async (req, res, next) => {
  try {
    const sql = `
      SELECT al.*, u.email AS user_email 
      FROM audit_logs al 
      LEFT JOIN users u ON al.actor_user_id = u.id 
      ORDER BY al.created_at DESC 
      LIMIT 100
    `;
    const result = await pool.query(sql);
    res.json({ success: true, count: result.rows.length, auditLogs: result.rows });
  } catch (err) {
    next(err);
  }
};

const getSharingDiagnostics = async (req, res, next) => {
  try {
    const statusCountsRes = await pool.query(`
      SELECT 
        status, 
        COUNT(*)::int AS count 
      FROM partner_connections 
      GROUP BY status
    `);
    const statusCounts = {};
    statusCountsRes.rows.forEach(r => { statusCounts[r.status] = r.count; });

    const relationshipDistRes = await pool.query(`
      SELECT 
        COALESCE(requester_relationship, relationship, 'Unspecified') AS rel_type,
        COUNT(*)::int AS count
      FROM partner_connections
      WHERE status = 'ACCEPTED'
      GROUP BY rel_type
      ORDER BY count DESC
    `);

    const permStatsRes = await pool.query(`
      SELECT 
        permission_type,
        COUNT(*)::int AS total_records,
        COUNT(*) FILTER (WHERE enabled = true)::int AS granted_count
      FROM partner_permissions
      GROUP BY permission_type
      ORDER BY granted_count DESC
    `);

    const auditRes = await pool.query(`
      SELECT 
        sae.id,
        sae.connection_id,
        sae.event_type,
        sae.target_user_id,
        sae.metadata,
        sae.created_at,
        actor.email AS actor_email
      FROM sharing_audit_events sae
      LEFT JOIN users actor ON sae.actor_id = actor.id
      ORDER BY sae.created_at DESC
      LIMIT 50
    `);

    res.json({
      success: true,
      diagnostics: {
        totalConnections: Object.values(statusCounts).reduce((a, b) => a + b, 0),
        statusBreakdown: statusCounts,
        relationshipDistribution: relationshipDistRes.rows,
        permissionStats: permStatsRes.rows,
        recentAuditEvents: auditRes.rows
      }
    });
  } catch (err) {
    next(err);
  }
};

module.exports = {
  getDashboardStats,
  getUsers,
  updateUserStatus,
  updateUserTag,
  getUserCycleLogs,
  getAdminProducts,
  createProduct,
  updateProduct,
  deleteProduct,
  getAdminOrders,
  updateOrderStatus,
  getAdminDeliveries,
  getChatLogs,
  getAuditLogs,
  getSharingDiagnostics
};
