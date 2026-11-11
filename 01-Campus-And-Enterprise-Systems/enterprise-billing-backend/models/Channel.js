import pool from "../config/database.js";

// Fetch all channels (ordered by sort_order)
export const getAllChannels = async () => {
    const [rows] = await pool.query(
        "SELECT * FROM channels ORDER BY sort_order ASC, name ASC"
    );
    return rows;
};

// Fetch single channel by ID
export const getChannelById = async (id) => {
    const [rows] = await pool.query(
        "SELECT * FROM channels WHERE id = ? LIMIT 1",
        [id]
    );
    return rows[0];
};

// Create a new channel
export const createChannel = async (data) => {
    const { name, slug, lcn, category, quality, accessType, logoFile, isActive, sortOrder } = data;

    const [result] = await pool.query(
        `INSERT INTO channels (name, slug, lcn, category, quality, access_type, logo_file, is_active, sort_order)
         VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)`,
        [name, slug, lcn, category, quality, accessType, logoFile, isActive ? 1 : 0, sortOrder || 0]
    );
    return result;
};

// Update an existing channel
export const updateChannel = async (id, data) => {
    const { name, slug, lcn, category, quality, accessType, logoFile, isActive, sortOrder } = data;

    const [result] = await pool.query(
        `UPDATE channels
         SET name = ?, slug = ?, lcn = ?, category = ?, quality = ?, access_type = ?, logo_file = ?, is_active = ?, sort_order = ?
         WHERE id = ?`,
        [name, slug, lcn, category, quality, accessType, logoFile, isActive ? 1 : 0, sortOrder || 0, id]
    );
    return result;
};

// Delete a channel
export const deleteChannel = async (id) => {
    const [result] = await pool.query(
        "DELETE FROM channels WHERE id = ?",
        [id]
    );
    return result;
};
