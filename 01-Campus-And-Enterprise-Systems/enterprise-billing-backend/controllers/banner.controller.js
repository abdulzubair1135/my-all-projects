import * as Banner from "../models/Banner.js";

/*
|--------------------------------------------------------------------------
| Get All Banners
|--------------------------------------------------------------------------
*/
export const getBanners = async (req, res) => {
    try {

        const banners = await Banner.getAllBanners();

        return res.status(200).json({
            success: true,
            count: banners.length,
            data: banners
        });

    } catch (err) {

        return res.status(500).json({
            success: false,
            message: err.message
        });

    }
};

/*
|--------------------------------------------------------------------------
| Get Banner By ID
|--------------------------------------------------------------------------
*/
export const getBannerById = async (req, res) => {
    try {

        const banner = await Banner.getBanner(req.params.id);

        if (!banner) {
            return res.status(404).json({
                success: false,
                message: "Banner not found"
            });
        }

        return res.status(200).json({
            success: true,
            data: banner
        });

    } catch (err) {

        return res.status(500).json({
            success: false,
            message: err.message
        });

    }
};

/*
|--------------------------------------------------------------------------
| Create Banner
|--------------------------------------------------------------------------
*/
export const createBanner = async (req, res) => {
    try {

        const result = await Banner.createBanner(req.body);

        return res.status(201).json({
            success: true,
            message: "Banner created successfully",
            id: result.insertId
        });

    } catch (err) {

        return res.status(500).json({
            success: false,
            message: err.message
        });

    }
};

/*
|--------------------------------------------------------------------------
| Update Banner
|--------------------------------------------------------------------------
*/
export const updateBanner = async (req, res) => {
    try {

        const result = await Banner.updateBanner(req.params.id, req.body);

        if (result.affectedRows === 0) {
            return res.status(404).json({
                success: false,
                message: "Banner not found"
            });
        }

        return res.status(200).json({
            success: true,
            message: "Banner updated successfully"
        });

    } catch (err) {

        return res.status(500).json({
            success: false,
            message: err.message
        });

    }
};

/*
|--------------------------------------------------------------------------
| Delete Banner
|--------------------------------------------------------------------------
*/
export const deleteBanner = async (req, res) => {
    try {

        const result = await Banner.deleteBanner(req.params.id);

        if (result.affectedRows === 0) {
            return res.status(404).json({
                success: false,
                message: "Banner not found"
            });
        }

        return res.status(200).json({
            success: true,
            message: "Banner deleted successfully"
        });

    } catch (err) {

        return res.status(500).json({
            success: false,
            message: err.message
        });

    }
};