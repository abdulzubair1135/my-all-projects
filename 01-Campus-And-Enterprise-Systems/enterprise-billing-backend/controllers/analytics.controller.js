import * as Analytics from "../models/Analytics.js";

export const getAnalytics = async (req, res) => {

    try {

        const data = await Analytics.getAnalytics();

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