import * as Channel from "../models/Channel.js";
import * as AuditLog from "../models/AuditLog.js";

// Retrieve all channels list
export const getChannels = async (req, res) => {
    try {
        const data = await Channel.getAllChannels();
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

// Retrieve single channel details
export const getChannel = async (req, res) => {
    try {
        const { id } = req.params;
        const data = await Channel.getChannelById(id);

        if (!data) {
            return res.status(404).json({
                success: false,
                message: "Channel not found."
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

// Create a new channel
export const createChannel = async (req, res) => {
    try {
        const result = await Channel.createChannel(req.body);

        // Audit Log
        await AuditLog.logAction(
            req.user?.id,
            "CREATE_CHANNEL",
            { channelName: req.body.name, channelId: result.insertId },
            req.ip
        );

        return res.status(201).json({
            success: true,
            message: "Channel created successfully!",
            id: result.insertId
        });
    } catch (err) {
        return res.status(500).json({
            success: false,
            message: err.message
        });
    }
};

// Update an existing channel
export const updateChannel = async (req, res) => {
    try {
        const { id } = req.params;
        await Channel.updateChannel(id, req.body);

        // Audit Log
        await AuditLog.logAction(
            req.user?.id,
            "UPDATE_CHANNEL",
            { channelId: id, channelName: req.body.name },
            req.ip
        );

        return res.status(200).json({
            success: true,
            message: "Channel updated successfully!"
        });
    } catch (err) {
        return res.status(500).json({
            success: false,
            message: err.message
        });
    }
};

// Delete a channel
export const deleteChannel = async (req, res) => {
    try {
        const { id } = req.params;
        await Channel.deleteChannel(id);

        // Audit Log
        await AuditLog.logAction(
            req.user?.id,
            "DELETE_CHANNEL",
            { channelId: id },
            req.ip
        );

        return res.status(200).json({
            success: true,
            message: "Channel deleted successfully!"
        });
    } catch (err) {
        return res.status(500).json({
            success: false,
            message: err.message
        });
    }
};
