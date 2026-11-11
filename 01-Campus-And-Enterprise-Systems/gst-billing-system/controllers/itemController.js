const Item = require('../models/itemModel');

const itemController = {
    getItems: async (req, res) => {
        try {
            const items = await Item.getAll();
            res.json(items);
        } catch (err) {
            res.status(500).json({ error: err.message });
        }
    }
};

module.exports = itemController;
