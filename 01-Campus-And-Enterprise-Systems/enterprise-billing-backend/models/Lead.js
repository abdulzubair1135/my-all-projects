import pool from "../config/database.js";

// Save a new lead from the public website
export const createLead = async (data) => {
    const { source, name, email, phone, message, metadata } = data;
    
    // Stringify metadata object to JSON string for database storage
    const metadataString = metadata ? JSON.stringify(metadata) : null;

    const [result] = await pool.query(
        `INSERT INTO leads (source, name, email, phone, message, metadata, status)
         VALUES (?, ?, ?, ?, ?, ?, 'new')`,
        [source, name, email, phone, message, metadataString]
    );

    return result;
};

// Retrieve leads list with search, status filters, and pagination
export const getLeads = async (filters) => {
    const { page = 1, limit = 10, search = "", status = "", source = "" } = filters;
    const offset = (page - 1) * limit;

    let query = "SELECT * FROM leads WHERE 1=1";
    const queryParams = [];

    // Filter by status if provided
    if (status) {
        query += " AND status = ?";
        queryParams.push(status);
    }

    // Filter by source if provided
    if (source) {
        query += " AND source = ?";
        queryParams.push(source);
    }

    // Filter by search text if provided
    if (search) {
        query += " AND (name LIKE ? OR email LIKE ? OR phone LIKE ? OR message LIKE ?)";
        const searchPattern = `%${search}%`;
        queryParams.push(searchPattern, searchPattern, searchPattern, searchPattern);
    }

    // Order by latest received leads
    query += " ORDER BY id DESC";

    // Get total count for pagination metadata
    const countQuery = query.replace("SELECT *", "SELECT COUNT(*) AS total");
    const [[{ total }]] = await pool.query(countQuery, queryParams);

    // Apply pagination limits
    query += " LIMIT ? OFFSET ?";
    queryParams.push(Number(limit), Number(offset));

    const [rows] = await pool.query(query, queryParams);

    // Parse JSON metadata for each row
    const leads = rows.map(row => {
        try {
            row.metadata = row.metadata ? JSON.parse(row.metadata) : null;
        } catch (e) {
            row.metadata = null;
        }
        return row;
    });

    return {
        leads,
        total,
        page: Number(page),
        limit: Number(limit),
        totalPages: Math.ceil(total / limit)
    };
};

// Update status of an enquiry (e.g. status: contacted, resolved)
export const updateLeadStatus = async (id, status) => {
    const [result] = await pool.query(
        "UPDATE leads SET status = ? WHERE id = ?",
        [status, id]
    );
    return result;
};

// Delete an enquiry record
export const deleteLead = async (id) => {
    const [result] = await pool.query(
        "DELETE FROM leads WHERE id = ?",
        [id]
    );
    return result;
};
