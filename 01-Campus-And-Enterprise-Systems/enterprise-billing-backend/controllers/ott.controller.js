import * as Ott from "../models/Ott.js";
import * as AuditLog from "../models/AuditLog.js";

/*
|--------------------------------------------------------------------------
| OTT Apps Actions
|--------------------------------------------------------------------------
*/

export const getApps = async (req, res) => {
    try {
        const data = await Ott.getAllApps();
        return res.status(200).json({ success: true, data });
    } catch (err) {
        return res.status(500).json({ success: false, message: err.message });
    }
};

export const getApp = async (req, res) => {
    try {
        const { id } = req.params;
        const data = await Ott.getAppById(id);
        if (!data) return res.status(404).json({ success: false, message: "OTT App not found." });
        return res.status(200).json({ success: true, data });
    } catch (err) {
        return res.status(500).json({ success: false, message: err.message });
    }
};

export const createApp = async (req, res) => {
    try {
        const result = await Ott.createApp(req.body);
        await AuditLog.logAction(req.user?.id, "CREATE_OTT_APP", { appName: req.body.name, appId: result.insertId }, req.ip);
        return res.status(201).json({ success: true, message: "OTT App created successfully!", id: result.insertId });
    } catch (err) {
        return res.status(500).json({ success: false, message: err.message });
    }
};

export const updateApp = async (req, res) => {
    try {
        const { id } = req.params;
        await Ott.updateApp(id, req.body);
        await AuditLog.logAction(req.user?.id, "UPDATE_OTT_APP", { appId: id, appName: req.body.name }, req.ip);
        return res.status(200).json({ success: true, message: "OTT App updated successfully!" });
    } catch (err) {
        return res.status(500).json({ success: false, message: err.message });
    }
};

export const deleteApp = async (req, res) => {
    try {
        const { id } = req.params;
        await Ott.deleteApp(id);
        await AuditLog.logAction(req.user?.id, "DELETE_OTT_APP", { appId: id }, req.ip);
        return res.status(200).json({ success: true, message: "OTT App deleted successfully!" });
    } catch (err) {
        return res.status(500).json({ success: false, message: err.message });
    }
};

/*
|--------------------------------------------------------------------------
| OTT Packages Actions
|--------------------------------------------------------------------------
*/

export const getPackages = async (req, res) => {
    try {
        const data = await Ott.getAllPackages();
        return res.status(200).json({ success: true, data });
    } catch (err) {
        return res.status(500).json({ success: false, message: err.message });
    }
};

export const getPackage = async (req, res) => {
    try {
        const { id } = req.params;
        const data = await Ott.getPackageById(id);
        if (!data) return res.status(404).json({ success: false, message: "OTT Package not found." });
        return res.status(200).json({ success: true, data });
    } catch (err) {
        return res.status(500).json({ success: false, message: err.message });
    }
};

export const createPackage = async (req, res) => {
    try {
        const result = await Ott.createPackage(req.body);
        await AuditLog.logAction(req.user?.id, "CREATE_OTT_PACKAGE", { packageName: req.body.name, packageId: result.insertId }, req.ip);
        return res.status(201).json({ success: true, message: "OTT Package created successfully!", id: result.insertId });
    } catch (err) {
        return res.status(500).json({ success: false, message: err.message });
    }
};

export const updatePackage = async (req, res) => {
    try {
        const { id } = req.params;
        await Ott.updatePackage(id, req.body);
        await AuditLog.logAction(req.user?.id, "UPDATE_OTT_PACKAGE", { packageId: id, packageName: req.body.name }, req.ip);
        return res.status(200).json({ success: true, message: "OTT Package updated successfully!" });
    } catch (err) {
        return res.status(500).json({ success: false, message: err.message });
    }
};

export const deletePackage = async (req, res) => {
    try {
        const { id } = req.params;
        await Ott.deletePackage(id);
        await AuditLog.logAction(req.user?.id, "DELETE_OTT_PACKAGE", { packageId: id }, req.ip);
        return res.status(200).json({ success: true, message: "OTT Package deleted successfully!" });
    } catch (err) {
        return res.status(500).json({ success: false, message: err.message });
    }
};

/*
|--------------------------------------------------------------------------
| Dish Billing Terms Actions
|--------------------------------------------------------------------------
*/

export const getBillingTerms = async (req, res) => {
    try {
        const data = await Ott.getAllBillingTerms();
        return res.status(200).json({ success: true, data });
    } catch (err) {
        return res.status(500).json({ success: false, message: err.message });
    }
};

export const getBillingTerm = async (req, res) => {
    try {
        const { id } = req.params;
        const data = await Ott.getBillingTermById(id);
        if (!data) return res.status(404).json({ success: false, message: "Billing term not found." });
        return res.status(200).json({ success: true, data });
    } catch (err) {
        return res.status(500).json({ success: false, message: err.message });
    }
};

export const createBillingTerm = async (req, res) => {
    try {
        const result = await Ott.createBillingTerm(req.body);
        await AuditLog.logAction(req.user?.id, "CREATE_BILLING_TERM", { termMonths: req.body.months, termId: result.insertId }, req.ip);
        return res.status(201).json({ success: true, message: "Billing term created successfully!", id: result.insertId });
    } catch (err) {
        return res.status(500).json({ success: false, message: err.message });
    }
};

export const updateBillingTerm = async (req, res) => {
    try {
        const { id } = req.params;
        await Ott.updateBillingTerm(id, req.body);
        await AuditLog.logAction(req.user?.id, "UPDATE_BILLING_TERM", { termId: id, termMonths: req.body.months }, req.ip);
        return res.status(200).json({ success: true, message: "Billing term updated successfully!" });
    } catch (err) {
        return res.status(500).json({ success: false, message: err.message });
    }
};

export const deleteBillingTerm = async (req, res) => {
    try {
        const { id } = req.params;
        await Ott.deleteBillingTerm(id);
        await AuditLog.logAction(req.user?.id, "DELETE_BILLING_TERM", { termId: id }, req.ip);
        return res.status(200).json({ success: true, message: "Billing term deleted successfully!" });
    } catch (err) {
        return res.status(500).json({ success: false, message: err.message });
    }
};
