// ============================================================
//
// AUTH ROUTES
//
// ============================================================

import express from "express";

import AuthController from "../controllers/Auth.js";

const router = express.Router();


// Login

router.post(

    "/login",

    AuthController.login

);


// Register

router.post(

    "/register",

    AuthController.register

);


// Profile

router.get(

    "/profile",

    AuthController.profile

);


export default router;