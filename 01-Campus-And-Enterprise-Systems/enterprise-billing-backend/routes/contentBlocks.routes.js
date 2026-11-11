import express from "express";
import auth from "../middleware/auth.js";
import {
    getBlocks,
    getSingleBlock,
    createBlock,
    updateBlock,
    deleteBlock
} from "../controllers/contentBlocks.controller.js";

const router = express.Router();

// Public reads
router.get("/block", getSingleBlock);

// Admin authenticated actions
router.get("/", auth, getBlocks);
router.post("/", auth, createBlock);
router.patch("/:id", auth, updateBlock);
router.delete("/:id", auth, deleteBlock);

export default router;
