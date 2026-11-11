import express from "express";
import auth from "../middleware/auth.js";
import {
    getChannels,
    getChannel,
    createChannel,
    updateChannel,
    deleteChannel
} from "../controllers/channels.controller.js";

const router = express.Router();

// Public reads
router.get("/", getChannels);
router.get("/:id", getChannel);

// Admin writes
router.post("/", auth, createChannel);
router.put("/:id", auth, updateChannel);
router.patch("/:id", auth, updateChannel);
router.delete("/:id", auth, deleteChannel);

export default router;
