const Bill = require('../models/billModel');
const Item = require('../models/itemModel');
const User = require('../models/userModel');

const billController = {
    createBill: async (req, res) => {
        try {
            const { customer_name, customer_state, customer_country, item_id } = req.body;
            const userId = req.session.userId;

            const user = await User.findById(userId);
            const item = await Item.findById(item_id);

            if (!user || !item) {
                return res.status(400).json({ success: false, message: 'Invalid User or Item' });
            }

            const price = parseFloat(item.price);
            let gst_type = 'None';
            let gst_percentage = 0;
            let gst_amount = 0;
            let final_amount = price;

            // GST Logic Rules
            if (customer_country.toLowerCase() !== 'india') {
                gst_type = 'Export (No GST)';
                gst_percentage = 0;
                gst_amount = 0;
                final_amount = price;
            } else if (customer_state.trim().toLowerCase() === user.state.trim().toLowerCase()) {
                gst_type = 'CGST + SGST';
                gst_percentage = 18; // 9% + 9%
                gst_amount = price * 0.18;
                final_amount = price + gst_amount;
            } else {
                gst_type = 'IGST';
                gst_percentage = 18;
                gst_amount = price * 0.18;
                final_amount = price + gst_amount;
            }

            const billId = await Bill.create({
                user_id: userId,
                item_id: item.id,
                customer_name,
                customer_state,
                customer_country,
                price,
                gst_type,
                gst_percentage,
                gst_amount,
                final_amount
            });

            res.json({ success: true, billId });
        } catch (err) {
            res.status(500).json({ success: false, message: err.message });
        }
    },

    getBillDetails: async (req, res) => {
        try {
            const bill = await Bill.findById(req.params.id);
            if (!bill) {
                return res.status(404).json({ success: false, message: 'Bill not found' });
            }
            res.json({ success: true, bill });
        } catch (err) {
            res.status(500).json({ success: false, message: err.message });
        }
    }
};

module.exports = billController;
