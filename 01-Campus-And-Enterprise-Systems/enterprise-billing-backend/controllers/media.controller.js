import fs from "fs";
import path from "path";
import pool from "../config/database.js";
import * as Media from "../models/Media.js";
import * as AuditLog from "../models/AuditLog.js";

// Fetch files from the media library
export const getMedia = async (req, res) => {
    try {
        const filters = {
            category: req.query.category || "all"
        };
        const data = await Media.getMedia(filters);
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

// Handle raw body uploads with metadata in headers
export const uploadRawMedia = async (req, res) => {
    try {
        // Retrieve and decode headers
        const originalNameEncoded = req.headers["x-file-name"] || "file";
        const originalName = decodeURIComponent(originalNameEncoded);
        const category = req.headers["x-media-category"] || "other";
        
        const altTextEncoded = req.headers["x-alt-text"] || "";
        const altText = decodeURIComponent(altTextEncoded);

        const mimeType = req.headers["content-type"];
        const size = req.body.length; // Length of the buffer in raw parser

        if (!req.body || size === 0) {
            return res.status(400).json({
                success: false,
                message: "No file content uploaded."
            });
        }

        // Generate unique filename on disk
        const filename = `${Date.now()}-${originalName.replace(/\s+/g, "_")}`;
        const uploadDir = path.join(process.cwd(), "uploads");

        // Ensure upload directory exists
        if (!fs.existsSync(uploadDir)) {
            fs.mkdirSync(uploadDir, { recursive: true });
        }

        const destPath = path.join(uploadDir, filename);

        // Save raw buffer to disk
        fs.writeFileSync(destPath, req.body);

        // Save to database
        const result = await Media.createMedia({
            filename,
            originalName,
            mimeType,
            size,
            category,
            altText
        });

        // Audit Log
        await AuditLog.logAction(
            req.user?.id,
            "UPLOAD_MEDIA",
            { filename, category },
            req.ip
        );

        return res.status(201).json({
            success: true,
            message: "File uploaded successfully!",
            id: result.insertId,
            data: {
                id: result.insertId,
                filename,
                original_name: originalName,
                mime_type: mimeType,
                size,
                category,
                alt_text: altText
            }
        });
    } catch (err) {
        return res.status(500).json({
            success: false,
            message: err.message
        });
    }
};

// Delete media asset
export const deleteMedia = async (req, res) => {
    try {
        const { id } = req.params;

        // Fetch media item to delete its file from disk
        const [rows] = await pool.query("SELECT * FROM media WHERE id = ? LIMIT 1", [id]);
        if (rows.length > 0) {
            const mediaItem = rows[0];
            const filePath = path.join(process.cwd(), "uploads", mediaItem.filename);
            if (fs.existsSync(filePath)) {
                fs.unlinkSync(filePath);
            }
        }

        await Media.deleteMedia(id);

        // Audit Log
        await AuditLog.logAction(
            req.user?.id,
            "DELETE_MEDIA",
            { mediaId: id },
            req.ip
        );

        return res.status(200).json({
            success: true,
            message: "Media item deleted successfully."
        });
    } catch (err) {
        return res.status(500).json({
            success: false,
            message: err.message
        });
    }
};
