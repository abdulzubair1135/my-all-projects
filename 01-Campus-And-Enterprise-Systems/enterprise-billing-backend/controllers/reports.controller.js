import * as Order from "../models/Order.js";

// Fetch compiled metrics for reports charts
export const getReportsOverview = async (req, res) => {
    try {
        const stats = await Order.getOrderStats();

        return res.status(200).json({
            success: true,
            data: {
                totalOrders: stats.total,
                pendingOrders: stats.pending,
                completedOrders: stats.completed,
                cancelledOrders: stats.cancelled,
                statusDistribution: stats.byStatus,
                dailyTrends: stats.dailyStats,
                packagePerformance: stats.packageStats
            }
        });
    } catch (err) {
        return res.status(500).json({
            success: false,
            message: err.message
        });
    }
};
