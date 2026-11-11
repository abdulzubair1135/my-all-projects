import * as ContentBlock from "../models/ContentBlock.js";
import * as AuditLog from "../models/AuditLog.js";

// Fetch paginated content blocks list
export const getBlocks = async (req, res) => {
    try {
        const filters = {
            page: req.query.page || 1,
            limit: req.query.limit || 10,
            search: req.query.search || ""
        };

        const result = await ContentBlock.getContentBlocks(filters);
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

// Public route to get a single block's content for display
export const getSingleBlock = async (req, res) => {
    try {
        const { pageKey, blockKey } = req.query;
        if (!pageKey || !blockKey) {
            return res.status(400).json({
                success: false,
                message: "pageKey and blockKey are required parameters."
            });
        }

        const data = await ContentBlock.getBlock(pageKey, blockKey);
        if (!data) {
            return res.status(404).json({
                success: false,
                message: "Block not found."
            });
        }

        return res.status(200).json({
            success: true,
            data
        });
    } catch (err) {
        return res.status(500).json({
            success: false,
            message: err.message
        });
    }
};

// Create a new content block
export const createBlock = async (req, res) => {
    try {
        const result = await ContentBlock.createBlock(req.body, req.user?.id);

        // Audit Log
        await AuditLog.logAction(
            req.user?.id,
            "CREATE_CONTENT_BLOCK",
            { pageKey: req.body.pageKey, blockKey: req.body.blockKey },
            req.ip
        );

        return res.status(201).json({
            success: true,
            message: "Content block created successfully!",
            id: result.insertId
        });
    } catch (err) {
        return res.status(500).json({
            success: false,
            message: err.message
        });
    }
};

// Update content block content
export const updateBlock = async (req, res) => {
    try {
        const { id } = req.params;
        await ContentBlock.updateBlock(id, req.body, req.user?.id);

        // Audit Log
        await AuditLog.logAction(
            req.user?.id,
            "UPDATE_CONTENT_BLOCK",
            { blockId: id },
            req.ip
        );

        return res.status(200).json({
            success: true,
            message: "Content block updated successfully!"
        });
    } catch (err) {
        return res.status(500).json({
            success: false,
            message: err.message
        });
    }
};

// Delete a content block
export const deleteBlock = async (req, res) => {
    try {
        const { id } = req.params;
        await ContentBlock.deleteBlock(id);

        // Audit Log
        await AuditLog.logAction(
            req.user?.id,
            "DELETE_CONTENT_BLOCK",
            { blockId: id },
            req.ip
        );

        return res.status(200).json({
            success: true,
            message: "Content block deleted successfully!"
        });
    } catch (err) {
        return res.status(500).json({
            success: false,
            message: err.message
        });
    }
};
