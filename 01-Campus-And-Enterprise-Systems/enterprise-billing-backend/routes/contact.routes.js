import express from "express";
import auth from "../middleware/auth.js";

import {
    getContacts,
    getContactById,
    createContact,
    deleteContact
} from "../controllers/contact.controller.js";

const router = express.Router();

// Public
router.post("/", createContact);

// Admin
router.get("/", auth, getContacts);
router.get("/:id", auth, getContactById);
router.delete("/:id", auth, deleteContact);

export default router;