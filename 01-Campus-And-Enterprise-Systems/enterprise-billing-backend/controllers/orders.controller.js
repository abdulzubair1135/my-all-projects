import * as Order from "../models/Order.js";
import * as AuditLog from "../models/AuditLog.js";

// Fetch paginated list of orders (Admin)
export const getOrders = async (req, res) => {
    try {
        const filters = {
            page: req.query.page || 1,
            limit: req.query.limit || 10,
            search: req.query.search || "",
            status: req.query.status || ""
        };

        const result = await Order.getOrders(filters);
        return res.status(200).json({
            success: true,
            data: result.data,
            meta: result.meta
        });
    } catch (err) {
        return res.status(500).json({
            success: false,
            message: err.message
        });
    }
};

// Update order status (Admin)
export const updateOrderStatus = async (req, res) => {
    try {
        const { id } = req.params;
        const { status } = req.body;

        if (!status) {
            return res.status(400).json({
                success: false,
                message: "Status field is required."
            });
        }

        await Order.updateOrderStatus(id, status);

        // Audit Log
        await AuditLog.logAction(
            req.user?.id,
            "UPDATE_ORDER_STATUS",
            { orderId: id, newStatus: status },
            req.ip
        );

        return res.status(200).json({
            success: true,
            message: "Order status updated successfully."
        });
    } catch (err) {
        return res.status(500).json({
            success: false,
            message: err.message
        });
    }
};

// Delete an order record (Admin)
export const deleteOrder = async (req, res) => {
    try {
        const { id } = req.params;
        await Order.deleteOrder(id);

        // Audit Log
        await AuditLog.logAction(
            req.user?.id,
            "DELETE_ORDER",
            { orderId: id },
            req.ip
        );

        return res.status(200).json({
            success: true,
            message: "Order deleted successfully."
        });
    } catch (err) {
        return res.status(500).json({
            success: false,
            message: err.message
        });
    }
};

// Get stats for order dashboard (Admin)
export const getStats = async (req, res) => {
    try {
        const result = await Order.getOrderStats();
        return res.status(200).json({
            success: true,
            data: result
        });
    } catch (err) {
        return res.status(500).json({
            success: false,
            message: err.message
        });
    }
};
