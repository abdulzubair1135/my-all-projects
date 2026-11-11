import express from "express";
import auth from "../middleware/auth.js";
import { login, logout, me, refresh } from "../controllers/auth.controller.js";

const router = express.Router();

// Public login & token refresh routes
router.post("/login", login);
router.post("/refresh", refresh);

// Protected routes
router.get("/me", auth, me);
router.post("/logout", auth, logout);

export default router;