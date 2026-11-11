import * as Lead from "../models/Lead.js";
import * as AuditLog from "../models/AuditLog.js";

// Public route to submit contact or audit enquiries
export const createPublicLead = async (req, res) => {
    try {
        const { source, name, email, phone, message, metadata } = req.body;

        // Basic Validation
        if (!source || !name || !phone) {
            return res.status(400).json({
                success: false,
                message: "Source, Name, and Phone number are required."
            });
        }

        const result = await Lead.createLead({ source, name, email, phone, message, metadata });

        return res.status(201).json({
            success: true,
            message: "Your request has been sent successfully!",
            id: result.insertId
        });
    } catch (err) {
        return res.status(500).json({
            success: false,
            message: err.message
        });
    }
};

// Admin route to retrieve all leads (paginated/filtered)
export const getLeads = async (req, res) => {
    try {
        const filters = {
            page: req.query.page || 1,
            limit: req.query.limit || 10,
            search: req.query.search || "",
            status: req.query.status || "",
            source: req.query.source || ""
        };

        const result = await Lead.getLeads(filters);

        return res.status(200).json({
            success: true,
            data: result.leads,
            meta: {
                page: result.page,
                limit: result.limit,
                total: result.total,
                totalPages: result.totalPages
            }
        });
    } catch (err) {
        return res.status(500).json({
            success: false,
            message: err.message
        });
    }
};

// Admin route to update lead status
export const updateLead = async (req, res) => {
    try {
        const { id } = req.params;
        const { status } = req.body;

        if (!status) {
            return res.status(400).json({
                success: false,
                message: "Status field is required."
            });
        }

        await Lead.updateLeadStatus(id, status);

        // Audit Log
        await AuditLog.logAction(
            req.user?.id,
            "UPDATE_LEAD_STATUS",
            { leadId: id, newStatus: status },
            req.ip
        );

        return res.status(200).json({
            success: true,
            message: "Enquiry status updated successfully."
        });
    } catch (err) {
        return res.status(500).json({
            success: false,
            message: err.message
        });
    }
};

// Admin route to delete lead record
export const deleteLead = async (req, res) => {
    try {
        const { id } = req.params;

        await Lead.deleteLead(id);

        // Audit Log
        await AuditLog.logAction(
            req.user?.id,
            "DELETE_LEAD",
            { leadId: id },
            req.ip
        );

        return res.status(200).json({
            success: true,
            message: "Enquiry deleted successfully."
        });
    } catch (err) {
        return res.status(500).json({
            success: false,
            message: err.message
        });
    }
};
