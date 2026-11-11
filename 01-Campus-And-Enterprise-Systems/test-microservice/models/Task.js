import pool from "../config/database.js";

class TaskModel {

    // Get all tasks
    async getAll() {
        const [rows] = await pool.query(`
            SELECT
                id,
                Detail,
                emp_id
            FROM tasks
            ORDER BY id DESC
        `);

        return rows;
    }

    // Get one task
    async getById(id) {
        const [rows] = await pool.query(
            `
            SELECT
                id,
                Detail,
                emp_id
            FROM tasks
            WHERE id = ?
            `,
            [id]
        );

        return rows[0];
    }

    // Create task
    async create(Detail, emp_id) {
        const [result] = await pool.query(
            `
            INSERT INTO tasks (Detail, emp_id)
            VALUES (?, ?)
            `,
            [Detail, emp_id]
        );

        return this.getById(result.insertId);
    }

    // Update task
    async update(id, Detail, emp_id) {
        const [result] = await pool.query(
            `
            UPDATE tasks
            SET Detail = ?, emp_id = ?
            WHERE id = ?
            `,
            [Detail, emp_id, id]
        );

        if (result.affectedRows === 0) {
            return null;
        }

        return this.getById(id);
    }

    // Delete task
    async delete(id) {
        const [result] = await pool.query(
            `
            DELETE FROM tasks
            WHERE id = ?
            `,
            [id]
        );

        return result.affectedRows > 0;
    }
}

export default new TaskModel();