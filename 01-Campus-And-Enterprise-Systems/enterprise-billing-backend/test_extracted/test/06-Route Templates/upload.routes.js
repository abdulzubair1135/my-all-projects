// ============================================================
//
// IMAGE UPLOAD ROUTES
//
// ============================================================

import express from "express";

import upload from "../middleware/upload.js";

import UploadController from "../controllers/Upload.js";

const router = express.Router();


// Upload Image

router.post(

    "/",

    upload.single("image"),

    UploadController.upload

);


export default router;