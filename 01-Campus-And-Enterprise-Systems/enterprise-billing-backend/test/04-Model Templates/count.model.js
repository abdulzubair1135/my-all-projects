import pool from "../config/db.js";

class UserModel {

    async count() {

        const [rows] = await pool.query(

            `
            SELECT COUNT(*) total

            FROM users
            `

        );

        return rows[0];

    }

}

export default new UserModel();