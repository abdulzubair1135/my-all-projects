import express from "express";

import {
    body,
    param
} from "express-validator";

import {
    getTasks,
    getTaskById,
    createTask,
    updateTask,
    deleteTask
} from "../controllers/tasks.controller.js";

import auth from "../middleware/auth.js";

import {validate} from "../middleware/validator.js";


const router = express.Router();


// GET ALL TASKS

router.get(
    "/",
    auth,
    getTasks
);


// GET TASK BY ID

router.get(
    "/:id",
    auth,

    param("id")
        .isInt()
        .withMessage("Task ID must be a number"),

    validate,

    getTaskById
);


// CREATE TASK

router.post(
    "/",
    auth,

    body("Detail")
        .trim()
        .notEmpty()
        .withMessage("Task detail is required"),

    body("emp_id")
        .isInt()
        .withMessage("Employee ID must be a number"),

    validate,

    createTask
);


// UPDATE TASK

router.put(
    "/:id",
    auth,

    param("id")
        .isInt()
        .withMessage("Task ID must be a number"),

    body("Detail")
        .trim()
        .notEmpty()
        .withMessage("Task detail is required"),

    body("emp_id")
        .isInt()
        .withMessage("Employee ID must be a number"),

    validate,

    updateTask
);


// DELETE TASK

router.delete(
    "/:id",
    auth,

    param("id")
        .isInt()
        .withMessage("Task ID must be a number"),

    validate,

    deleteTask
);


export default router;