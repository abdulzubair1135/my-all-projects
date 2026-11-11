// ============================================================
// File Name : update.model.js
// Purpose   : UPDATE Existing Record
// Layer     : Model
// ============================================================

// Is file ka use database ke existing record ko update
// karne ke liye hota hai.
//
// Example:
//
// Edit User
// Edit Service
// Edit FAQ
// Edit Plan
//
// ============================================================

import pool from "../config/db.js";

class UserModel {

    // ========================================================
    // UPDATE USER
    //
    // SQL:
    // UPDATE users
    // SET name=?, email=?, phone=?
    // WHERE id=?
    //
    // Parameter:
    // id
    // data
    //
    // Return:
    // result
    // ========================================================

    async update(id, data) {

        const [result] = await pool.query(

            `
            UPDATE users

            SET

                name = ?,

                email = ?,

                phone = ?

            WHERE id = ?
            `,

            [

                data.name,

                data.email,

                data.phone,

                id

            ]

        );

        return result;

    }

}

export default new UserModel();