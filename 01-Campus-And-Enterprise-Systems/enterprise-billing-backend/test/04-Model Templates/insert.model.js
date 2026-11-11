// ============================================================
// File Name : insert.model.js
// Purpose   : INSERT New Record
// Layer     : Model
// ============================================================

// Is file ka use database me naya record insert karne ke liye hota hai.
//
// Example:
// Register User
// Add Service
// Add FAQ
// Add Plan
//
// ============================================================

import pool from "../config/db.js";

class UserModel {

    // ========================================================
    // CREATE NEW USER
    //
    // SQL:
    // INSERT INTO users(name,email,phone)
    // VALUES(?,?,?)
    //
    // Parameter:
    // data
    //
    // Return:
    // insertId
    // ========================================================

    async create(data) {

        const [result] = await pool.query(

            `
            INSERT INTO users

            (

                name,

                email,

                phone

            )

            VALUES

            (

                ?,

                ?,

                ?

            )
            `,

            [

                data.name,

                data.email,

                data.phone

            ]

        );

        return result.insertId;

    }

}

export default new UserModel();