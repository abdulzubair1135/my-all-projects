// ============================================================
// FILE NAME : User.js
// PURPOSE   : User Database Model
// ============================================================

import pool from "../config/database.js";


// ============================================================
// USER MODEL
// ============================================================

class User {


    // ========================================================
    // GET ALL USERS
    // ========================================================

    static async getAllUsers() {

        const [rows] = await pool.query(

            `SELECT 
                id,
                name,
                email,
                Task
             FROM emp`

        );

        return rows;

    }


    // ========================================================
    // FIND USER BY EMAIL
    // Login ke liye use hoga
    // ========================================================

    static async findUserByEmail(email) {

        const [rows] = await pool.query(

            `SELECT *
             FROM emp
             WHERE email = ?`,

            [email]

        );

        return rows[0];

    }


    // ========================================================
    // GET USER BY ID
    // ========================================================

    static async getUserById(id) {

        const [rows] = await pool.query(

            `SELECT
                id,
                name,
                email,
                Task
             FROM emp
             WHERE id = ?`,

            [id]

        );

        return rows[0];

    }


    // ========================================================
    // CREATE USER
    // ========================================================

    static async createUser(
        name,
        email,
        Task,
        password
    ) {

        const [result] = await pool.query(

            `INSERT INTO emp
                (name, email, Task, password)
             VALUES
                (?, ?, ?, ?)`,

            [
                name,
                email,
                Task,
                password
            ]

        );

        return result;

    }


    // ========================================================
    // UPDATE USER
    // ========================================================

    static async updateUser(
        id,
        name,
        email,
        Task
    ) {

        const [result] = await pool.query(

            `UPDATE emp
             SET
                name = ?,
                email = ?,
                Task = ?
             WHERE id = ?`,

            [
                name,
                email,
                Task,
                id
            ]

        );

        return result;

    }


    // ========================================================
    // DELETE USER
    // ========================================================

    static async deleteUser(id) {

        const [result] = await pool.query(

            `DELETE FROM emp
             WHERE id = ?`,

            [id]

        );

        return result;

    }

}


// ============================================================
// EXPORT
// ============================================================

export default User;