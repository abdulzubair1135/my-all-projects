import express from "express";
import auth from "../middleware/auth.js";
import { getMedia, uploadRawMedia, deleteMedia } from "../controllers/media.controller.js";

const router = express.Router();

// Get media items list
router.get("/", auth, getMedia);

// Upload raw body media with file size limit up to 10MB
router.post(
    "/",
    auth,
    express.raw({ type: "*/*", limit: "10mb" }),
    uploadRawMedia
);

// Delete media
router.delete("/:id", auth, deleteMedia);

export default router;
