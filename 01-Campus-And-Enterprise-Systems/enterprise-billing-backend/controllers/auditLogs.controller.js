import * as AuditLog from "../models/AuditLog.js";

// Fetch audit logs for compliance dashboard (Admin)
export const getLogs = async (req, res) => {
    try {
        const logs = await AuditLog.getAuditLogs();
        return res.status(200).json({
            success: true,
            data: logs
        });
    } catch (err) {
        return res.status(500).json({
            success: false,
            message: err.message
        });
    }
};
