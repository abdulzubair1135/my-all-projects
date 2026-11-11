// ============================================================
// File Name : select.model.js
// Purpose   : SELECT Query Template
// Layer     : Model
// ============================================================

// Model ka kaam sirf Database se baat karna hota hai.
// Is file me sirf SQL Queries hongi.
// req, res ya response yaha nahi likhte.

// ============================================================

import pool from "../config/db.js";

class UserModel {

    // ========================================================
    // GET ALL RECORDS
    //
    // SQL:
    // SELECT * FROM users;
    //
    // Return:
    // Array
    //
    // Use:
    // Controller -> Model -> Database
    // ========================================================

    async getAll() {

        const [rows] = await pool.query(`
            SELECT *
            FROM users
        `);

        return rows;

    }

}

export default new UserModel();