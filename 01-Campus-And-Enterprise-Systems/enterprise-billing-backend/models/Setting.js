import pool from "../config/database.js";

export const getSettings = async () => {

    const [rows] = await pool.query(
        "SELECT * FROM settings LIMIT 1"
    );

    return rows[0];

};

export const updateSettings = async (data) => {

    const {
        site_name,
        email,
        phone,
        address
    } = data;

    const [result] = await pool.query(

        `UPDATE settings
        SET
        site_name=?,
        email=?,
        phone=?,
        address=?
        WHERE id=1`,

        [
            site_name,
            email,
            phone,
            address
        ]

    );

    return result;

};