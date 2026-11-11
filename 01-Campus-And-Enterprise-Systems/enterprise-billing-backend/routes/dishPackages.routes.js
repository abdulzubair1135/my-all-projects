import express from "express";
import auth from "../middleware/auth.js";
import {
    getPackages,
    getPackage,
    createPackage,
    updatePackage,
    deletePackage
} from "../controllers/dishPackages.controller.js";

const router = express.Router();

// Publicly accessible reads
router.get("/", getPackages);
router.get("/:id", getPackage);

// Admin authenticated writes
router.post("/", auth, createPackage);
router.put("/:id", auth, updatePackage);
router.patch("/:id", auth, updatePackage);
router.delete("/:id", auth, deletePackage);

export default router;
