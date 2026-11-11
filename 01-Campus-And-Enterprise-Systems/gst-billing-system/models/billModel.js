const db = require('../config/db');

const Bill = {
    create: async (billData) => {
        const {
            user_id, item_id, customer_name, customer_state, customer_country,
            price, gst_type, gst_percentage, gst_amount, final_amount
        } = billData;

        const [result] = await db.query(
            `INSERT INTO bills (user_id, item_id, customer_name, customer_state, customer_country, price, gst_type, gst_percentage, gst_amount, final_amount) 
             VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`,
            [user_id, item_id, customer_name, customer_state, customer_country, price, gst_type, gst_percentage, gst_amount, final_amount]
        );
        return result.insertId;
    },
    findById: async (id) => {
        const [rows] = await db.query(`
            SELECT bills.*, users.name as seller_name, users.state as seller_state, users.country as seller_country, items.item_name 
            FROM bills 
            JOIN users ON bills.user_id = users.id 
            JOIN items ON bills.item_id = items.id 
            WHERE bills.id = ?
        `, [id]);
        return rows[0];
    }
};

module.exports = Bill;
