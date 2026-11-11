import pool from "../config/database.js";

// Fetch paginated content blocks
export const getContentBlocks = async (filters) => {
    const { page = 1, limit = 10, search = "" } = filters;
    const offset = (page - 1) * limit;

    let query = `
        SELECT cb.*, a.name AS updated_by_name 
        FROM content_blocks cb
        LEFT JOIN admin a ON cb.updated_by = a.id
        WHERE 1=1
    `;
    const queryParams = [];

    if (search) {
        query += " AND (cb.page_key LIKE ? OR cb.block_key LIKE ? OR cb.title LIKE ? OR cb.body LIKE ?)";
        const searchPattern = `%${search}%`;
        queryParams.push(searchPattern, searchPattern, searchPattern, searchPattern);
    }

    query += " ORDER BY cb.id DESC";

    const countQuery = `
        SELECT COUNT(*) AS total 
        FROM content_blocks cb
        WHERE 1=1
        ${search ? "AND (cb.page_key LIKE ? OR cb.block_key LIKE ? OR cb.title LIKE ? OR cb.body LIKE ?)" : ""}
    `;
    const [[{ total }]] = await pool.query(countQuery, search ? queryParams : []);

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

// Retrieve a single content block by page_key and block_key (for public frontend load)
export const getBlock = async (pageKey, blockKey) => {
    const [rows] = await pool.query(
        "SELECT * FROM content_blocks WHERE page_key = ? AND block_key = ? LIMIT 1",
        [pageKey, blockKey]
    );
    return rows[0];
};

// Create a new content block
export const createBlock = async (data, userId) => {
    const { pageKey, blockKey, title, body, contentType, isPublished } = data;

    const [result] = await pool.query(
        `INSERT INTO content_blocks (page_key, block_key, title, body, content_type, is_published, updated_by)
         VALUES (?, ?, ?, ?, ?, ?, ?)`,
        [pageKey, blockKey, title, body, contentType || "text", isPublished ? 1 : 0, userId || null]
    );
    return result;
};

// Update an existing content block
export const updateBlock = async (id, data, userId) => {
    const { title, body, contentType, isPublished } = data;

    const [result] = await pool.query(
        `UPDATE content_blocks
         SET title = ?, body = ?, content_type = ?, is_published = ?, updated_by = ?
         WHERE id = ?`,
        [title, body, contentType, isPublished ? 1 : 0, userId || null, id]
    );
    return result;
};

// Delete a content block
export const deleteBlock = async (id) => {
    const [result] = await pool.query("DELETE FROM content_blocks WHERE id = ?", [id]);
    return result;
};
