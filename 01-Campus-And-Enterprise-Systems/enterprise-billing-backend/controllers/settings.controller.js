import * as Setting from "../models/Setting.js";

export const getSettings = async (req, res) => {

    try {

        const data = await Setting.getSettings();

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

export const updateSettings = async (req, res) => {

    try {

        const result = await Setting.updateSettings(req.body);

        return res.status(200).json({
            success: true,
            message: "Settings updated successfully"
        });

    } catch (err) {

        return res.status(500).json({
            success: false,
            message: err.message
        });

    }

};