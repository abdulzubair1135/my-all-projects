import pool from "../config/database.js";

// Add a new log entry
export const logAction = async (userId, action, details, ipAddress) => {
    const [result] = await pool.query(
        `INSERT INTO audit_logs (user_id, action, details, ip_address)
         VALUES (?, ?, ?, ?)`,
        [userId, action, details ? JSON.stringify(details) : null, ipAddress || null]
    );
    return result;
};

// Fetch audit logs with admin user details
export const getAuditLogs = async () => {
    const [rows] = await pool.query(
        `SELECT al.*, a.name AS admin_name, a.email AS admin_email 
         FROM audit_logs al
         LEFT JOIN admin a ON al.user_id = a.id
         ORDER BY al.id DESC 
         LIMIT 100`
    );

    // Parse JSON details if any
    return rows.map(row => {
        try {
            row.details = row.details ? JSON.parse(row.details) : null;
        } catch (e) {
            row.details = null;
        }
        return row;
    });
};
