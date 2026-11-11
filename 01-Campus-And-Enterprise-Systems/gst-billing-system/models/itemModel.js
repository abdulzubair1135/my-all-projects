const db = require('../config/db');

const Item = {
    getAll: async () => {
        const [rows] = await db.query('SELECT * FROM items');
        return rows;
    },
    findById: async (id) => {
        const [rows] = await db.query('SELECT * FROM items WHERE id = ?', [id]);
        return rows[0];
    }
};

module.exports = Item;
