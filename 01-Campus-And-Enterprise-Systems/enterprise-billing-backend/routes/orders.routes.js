import express from "express";
import auth from "../middleware/auth.js";
import {
    getOrders,
    getStats,
    updateOrderStatus,
    deleteOrder
} from "../controllers/orders.controller.js";

const router = express.Router();

// Admin authenticated order actions
router.get("/", auth, getOrders);
router.get("/stats", auth, getStats);
router.patch("/:id", auth, updateOrderStatus);
router.delete("/:id", auth, deleteOrder);

export default router;
