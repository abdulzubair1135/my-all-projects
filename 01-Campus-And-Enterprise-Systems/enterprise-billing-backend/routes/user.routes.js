import express from "express";
import { body } from "express-validator";

import auth from "../middleware/auth.js";
import { validate } from "../middleware/validator.js";

import {
    getUsers,
    getUser,
    createUser,
    updateUser,
    deleteUser
} from "../controllers/user.controller.js";

const router = express.Router();

/*
|--------------------------------------------------------------------------
| GET ALL USERS
|--------------------------------------------------------------------------
*/
router.get("/", auth, getUsers);

/*
|--------------------------------------------------------------------------
| GET SINGLE USER
|--------------------------------------------------------------------------
*/
router.get("/:id", auth, getUser);

/*
|--------------------------------------------------------------------------
| CREATE USER
|--------------------------------------------------------------------------
*/
router.post(
    "/",
    auth,

    body("name")
        .notEmpty()
        .withMessage("Name is required"),

    body("email")
        .isEmail()
        .withMessage("Valid Email is required"),

    body("phone")
        .notEmpty()
        .withMessage("Phone is required"),

    body("password")
        .isLength({ min: 6 })
        .withMessage("Password must be at least 6 characters"),

    validate,

    createUser
);

/*
|--------------------------------------------------------------------------
| UPDATE USER
|--------------------------------------------------------------------------
*/
router.put(
    "/:id",
    auth,

    body("name")
        .optional()
        .notEmpty(),

    body("email")
        .optional()
        .isEmail(),

    body("phone")
        .optional()
        .notEmpty(),

    validate,

    updateUser
);

/*
|--------------------------------------------------------------------------
| DELETE USER
|--------------------------------------------------------------------------
*/
router.delete("/:id", auth, deleteUser);

export default router;