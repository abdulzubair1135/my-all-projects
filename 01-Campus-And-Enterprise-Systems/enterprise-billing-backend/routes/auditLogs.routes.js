import express from "express";
import auth from "../middleware/auth.js";
import { getLogs } from "../controllers/auditLogs.controller.js";

const router = express.Router();

// Retrieve logs index
router.get("/", auth, getLogs);

export default router;
