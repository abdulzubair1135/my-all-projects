import pool from "../config/database.js";

export const findByEmail = async (email) => {

    const [rows] = await pool.query(

        "SELECT * FROM admin WHERE email=? LIMIT 1",

        [email]

    );

    return rows[0];

};

export const findById = async (id) => {

    const [rows] = await pool.query(

        "SELECT * FROM admin WHERE id=? LIMIT 1",

        [id]

    );

    return rows[0];

};

export const updateLastLogin = async (id) => {

    await pool.query(

        "UPDATE admin SET last_login=NOW() WHERE id=?",

        [id]

    );

};