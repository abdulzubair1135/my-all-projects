import express from "express";
import auth from "../middleware/auth.js";

import {
    getSettings,
    updateSettings
} from "../controllers/settings.controller.js";

const router = express.Router();

router.get("/", auth, getSettings);

router.put("/", auth, updateSettings);

export default router;