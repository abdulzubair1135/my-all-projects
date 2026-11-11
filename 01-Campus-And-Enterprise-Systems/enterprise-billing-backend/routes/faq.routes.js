import express from "express";
import auth from "../middleware/auth.js";

import {

    getFaqs,
    getFaqById,
    createFaq,
    updateFaq,
    deleteFaq

} from "../controllers/faq.controller.js";

const router = express.Router();

router.get("/", getFaqs);

router.get("/:id", getFaqById);

router.post("/", auth, createFaq);

router.put("/:id", auth, updateFaq);

router.delete("/:id", auth, deleteFaq);

export default router;