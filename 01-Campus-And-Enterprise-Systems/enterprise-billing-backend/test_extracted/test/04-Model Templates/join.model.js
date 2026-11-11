import pool from "../config/db.js";

class UserModel {

    async getAll() {

        const [rows] = await pool.query(

            `
            SELECT

            users.*,

            roles.name AS role_name

            FROM users

            LEFT JOIN roles

            ON users.role_id=roles.id
            `

        );

        return rows;

    }

}

export default new UserModel();