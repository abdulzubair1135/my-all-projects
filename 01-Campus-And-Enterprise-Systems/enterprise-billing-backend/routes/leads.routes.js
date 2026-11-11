import express from "express";
import auth from "../middleware/auth.js";
import {
    createPublicLead,
    getLeads,
    updateLead,
    deleteLead
} from "../controllers/leads.controller.js";

const router = express.Router();

// Public submission route
router.post("/public", createPublicLead);

// Admin authenticated management routes
router.get("/", auth, getLeads);
router.patch("/:id", auth, updateLead);
router.delete("/:id", auth, deleteLead);

export default router;
