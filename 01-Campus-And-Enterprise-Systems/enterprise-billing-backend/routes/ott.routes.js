import express from "express";
import auth from "../middleware/auth.js";
import {
    getApps, getApp, createApp, updateApp, deleteApp,
    getPackages, getPackage, createPackage, updatePackage, deletePackage,
    getBillingTerms, getBillingTerm, createBillingTerm, updateBillingTerm, deleteBillingTerm
} from "../controllers/ott.controller.js";

const router = express.Router();

/*
|--------------------------------------------------------------------------
| OTT Apps Routes
|--------------------------------------------------------------------------
*/
router.get("/ott-apps", getApps);
router.get("/ott-apps/:id", getApp);
router.post("/ott-apps", auth, createApp);
router.patch("/ott-apps/:id", auth, updateApp);
router.delete("/ott-apps/:id", auth, deleteApp);

/*
|--------------------------------------------------------------------------
| OTT Packages Routes
|--------------------------------------------------------------------------
*/
router.get("/ott-packages", getPackages);
router.get("/ott-packages/:id", getPackage);
router.post("/ott-packages", auth, createPackage);
router.patch("/ott-packages/:id", auth, updatePackage);
router.delete("/ott-packages/:id", auth, deletePackage);

/*
|--------------------------------------------------------------------------
| Dish Billing Terms Routes
|--------------------------------------------------------------------------
*/
router.get("/dish-billing-terms", getBillingTerms);
router.get("/dish-billing-terms/:id", getBillingTerm);
router.post("/dish-billing-terms", auth, createBillingTerm);
router.patch("/dish-billing-terms/:id", auth, updateBillingTerm);
router.delete("/dish-billing-terms/:id", auth, deleteBillingTerm);

export default router;
