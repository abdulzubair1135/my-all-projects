// ============================================================
// File Name : delete.model.js
// Purpose   : DELETE Record
// Layer     : Model
// ============================================================

// Is file ka use database se record delete karne ke liye hota hai.
//
// Example:
//
// Delete User
// Delete Service
// Delete Banner
// Delete FAQ
//
// ============================================================

import pool from "../config/db.js";

class UserModel {

    // ========================================================
    // DELETE USER
    //
    // SQL:
    // DELETE FROM users WHERE id=?
    //
    // Parameter:
    // id
    //
    // Return:
    // result
    // ========================================================

    async delete(id) {

        const [result] = await pool.query(

            `
            DELETE FROM users

            WHERE id=?
            `,

            [

                id

            ]

        );

        return result;

    }

}

export default new UserModel();