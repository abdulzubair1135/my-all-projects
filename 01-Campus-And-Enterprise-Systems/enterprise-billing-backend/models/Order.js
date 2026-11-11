import pool from "../config/database.js";

// Fetch paginated list of orders
export const getOrders = async (filters) => {
    const { page = 1, limit = 10, search = "", status = "" } = filters;
    const offset = (page - 1) * limit;

    let query = "SELECT * FROM orders WHERE 1=1";
    const queryParams = [];

    if (status) {
        query += " AND status = ?";
        queryParams.push(status);
    }

    if (search) {
        query += " AND (name LIKE ? OR email LIKE ? OR phone LIKE ? OR city LIKE ?)";
        const searchPattern = `%${search}%`;
        queryParams.push(searchPattern, searchPattern, searchPattern, searchPattern);
    }

    query += " ORDER BY id DESC";

    const countQuery = query.replace("SELECT *", "SELECT COUNT(*) AS total");
    const [[{ total }]] = await pool.query(countQuery, queryParams);

    query += " LIMIT ? OFFSET ?";
    queryParams.push(Number(limit), Number(offset));

    const [rows] = await pool.query(query, queryParams);

    return {
        data: rows,
        meta: {
            page: Number(page),
            limit: Number(limit),
            total,
            totalPages: Math.ceil(total / limit)
        }
    };
};

// Fetch single order details
export const getOrderById = async (id) => {
    const [rows] = await pool.query("SELECT * FROM orders WHERE id = ? LIMIT 1", [id]);
    return rows[0];
};

// Create a new order
export const createOrder = async (data) => {
    const { name, email, phone, address, city, message, packageId, packageType, months, price } = data;

    const [result] = await pool.query(
        `INSERT INTO orders 
        (name, email, phone, address, city, message, package_id, package_type, months, price, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'pending')`,
        [name, email, phone, address, city, message, packageId, packageType, months, price]
    );

    return result;
};

// Update order status
export const updateOrderStatus = async (id, status) => {
    const [result] = await pool.query(
        "UPDATE orders SET status = ? WHERE id = ?",
        [status, id]
    );
    return result;
};

// Delete an order
export const deleteOrder = async (id) => {
    const [result] = await pool.query("DELETE FROM orders WHERE id = ?", [id]);
    return result;
};

// Calculate order pipeline stats and activity for reports
export const getOrderStats = async () => {
    // 1. Get counts by status
    const [[{ total }]] = await pool.query("SELECT COUNT(*) AS total FROM orders");
    const [[{ pending }]] = await pool.query("SELECT COUNT(*) AS pending FROM orders WHERE status = 'pending'");
    const [[{ completed }]] = await pool.query("SELECT COUNT(*) AS completed FROM orders WHERE status = 'completed'");
    const [[{ cancelled }]] = await pool.query("SELECT COUNT(*) AS cancelled FROM orders WHERE status = 'cancelled'");

    // 2. Get breakdown list for status pipeline
    const statuses = ['pending', 'approved', 'completed', 'cancelled'];
    const byStatus = [];
    for (let status of statuses) {
        const [[{ count }]] = await pool.query("SELECT COUNT(*) AS count FROM orders WHERE status = ?", [status]);
        byStatus.push({ status, count });
    }

    // 3. Get daily orders count for the last 30 days (for the chart)
    const [dailyRows] = await pool.query(`
        SELECT DATE_FORMAT(created_at, '%Y-%m-%d') AS day, COUNT(*) AS orders
        FROM orders
        WHERE created_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)
        GROUP BY day
        ORDER BY day ASC
    `);

    // 4. Get package activity stats
    // We group orders by package name (could be mapped from dish_packages)
    const [packageRows] = await pool.query(`
        SELECT 
            COALESCE(dp.name, 'Custom Package') AS packageName,
            COUNT(o.id) AS orders,
            SUM(CASE WHEN o.status = 'completed' THEN 1 ELSE 0 END) AS completed,
            SUM(CASE WHEN o.status = 'completed' THEN COALESCE(o.price, 0) ELSE 0 END) AS verifiedValue
        FROM orders o
        LEFT JOIN dish_packages dp ON o.package_id = o.package_id AND o.package_type = 'dish'
        GROUP BY packageName
        ORDER BY orders DESC
    `);

    return {
        total,
        pending,
        completed,
        cancelled,
        byStatus,
        dailyStats: dailyRows,
        packageStats: packageRows
    };
};
