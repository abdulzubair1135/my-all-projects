// ============================================================
// FILE NAME : user.routes.js
// ============================================================

import express from "express";

import auth from "../middleware/auth.js";

import {
    getUsers,
    getUserById
} from "../controllers/user.controller.js";


const router = express.Router();


// ============================================================
// GET ALL USERS
// ============================================================

router.get(
    "/",
    auth,
    getUsers
);


// ============================================================
// GET USER BY ID
// ============================================================

router.get(
    "/:id",
    auth,
    getUserById
);


export default router;