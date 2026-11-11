import express from "express";
import auth from "../middleware/auth.js";
import { getReportsOverview } from "../controllers/reports.controller.js";

const router = express.Router();

// Retrieve reports overview
router.get("/overview", auth, getReportsOverview);

export default router;
