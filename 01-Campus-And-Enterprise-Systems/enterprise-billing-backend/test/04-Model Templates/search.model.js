import pool from "../config/db.js";

class UserModel {

    async search(keyword) {

        const [rows] = await pool.query(

            `
            SELECT *

            FROM users

            WHERE

            name LIKE ?

            `,

            [

                `%${keyword}%`

            ]

        );

        return rows;

    }

}

export default new UserModel();