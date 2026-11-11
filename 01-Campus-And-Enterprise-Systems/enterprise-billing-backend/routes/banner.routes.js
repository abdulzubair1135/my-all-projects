import express from "express";

import auth from "../middleware/auth.js";

import {
    getBanners,
    getBannerById,
    createBanner,
    updateBanner,
    deleteBanner
} from "../controllers/banner.controller.js";

const router = express.Router();

/*
|--------------------------------------------------------------------------
| Public Routes
|--------------------------------------------------------------------------
*/

router.get("/", getBanners);
router.get("/:id", getBannerById);

/*
|--------------------------------------------------------------------------
| Protected Routes
|--------------------------------------------------------------------------
*/

router.post("/", auth, createBanner);
router.put("/:id", auth, updateBanner);
router.delete("/:id", auth, deleteBanner);

export default router;