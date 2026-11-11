import pool from "../config/database.js";

// Save uploaded file metadata to the database
export const createMedia = async (data) => {
    const { filename, originalName, mimeType, size, category, altText } = data;

    const [result] = await pool.query(
        `INSERT INTO media (filename, original_name, mime_type, size, category, alt_text)
         VALUES (?, ?, ?, ?, ?, ?)`,
        [filename, originalName, mimeType, size, category || 'other', altText || null]
    );
    return result;
};

// Retrieve media library files, filterable by category
export const getMedia = async (filters) => {
    const { category = "" } = filters;
    
    let query = "SELECT * FROM media";
    const queryParams = [];

    if (category && category !== "all") {
        query += " WHERE category = ?";
        queryParams.push(category);
    }

    query += " ORDER BY id DESC";

    const [rows] = await pool.query(query, queryParams);
    return rows;
};

// Delete media metadata
export const deleteMedia = async (id) => {
    const [result] = await pool.query("DELETE FROM media WHERE id = ?", [id]);
    return result;
};
