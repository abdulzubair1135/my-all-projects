import * as DishPackage from "../models/DishPackage.js";
import * as AuditLog from "../models/AuditLog.js";

// Fetch all dish packages (public / admin)
export const getPackages = async (req, res) => {
    try {
        const data = await DishPackage.getAllPackages();
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

// Fetch single dish package details
export const getPackage = async (req, res) => {
    try {
        const { id } = req.params;
        const data = await DishPackage.getPackageById(id);

        if (!data) {
            return res.status(404).json({
                success: false,
                message: "Package not found."
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

// Create a new package
export const createPackage = async (req, res) => {
    try {
        const result = await DishPackage.createPackage(req.body);

        // Audit Log
        await AuditLog.logAction(
            req.user?.id,
            "CREATE_DISH_PACKAGE",
            { packageName: req.body.name, packageId: result.insertId },
            req.ip
        );

        return res.status(201).json({
            success: true,
            message: "Package created successfully!",
            id: result.insertId
        });
    } catch (err) {
        return res.status(500).json({
            success: false,
            message: err.message
        });
    }
};

// Update an existing package
export const updatePackage = async (req, res) => {
    try {
        const { id } = req.params;
        const result = await DishPackage.updatePackage(id, req.body);

        // Audit Log
        await AuditLog.logAction(
            req.user?.id,
            "UPDATE_DISH_PACKAGE",
            { packageId: id, packageName: req.body.name },
            req.ip
        );

        return res.status(200).json({
            success: true,
            message: "Package updated successfully!"
        });
    } catch (err) {
        return res.status(500).json({
            success: false,
            message: err.message
        });
    }
};

// Delete a package
export const deletePackage = async (req, res) => {
    try {
        const { id } = req.params;
        await DishPackage.deletePackage(id);

        // Audit Log
        await AuditLog.logAction(
            req.user?.id,
            "DELETE_DISH_PACKAGE",
            { packageId: id },
            req.ip
        );

        return res.status(200).json({
            success: true,
            message: "Package deleted successfully!"
        });
    } catch (err) {
        return res.status(500).json({
            success: false,
            message: err.message
        });
    }
};
