// ============================================================
// File Name : selectById.model.js
// Purpose   : SELECT Single Record by ID
// Layer     : Model
// ============================================================

// Is file ka use ek hi record lane ke liye hota hai.
// Example:
// GET /users/1
// GET /services/5
// GET /faqs/3

// ============================================================

import pool from "../config/db.js";

class UserModel {

    // ========================================================
    // GET RECORD BY ID
    //
    // SQL:
    // SELECT * FROM users WHERE id=?
    //
    // Return:
    // Object
    //
    // Parameter:
    // id
    //
    // ========================================================

    async getById(id) {

        const [rows] = await pool.query(

            `
            SELECT *

            FROM users

            WHERE id=?
            `,

            [id]

        );

        return rows[0];

    }

}

export default new UserModel();