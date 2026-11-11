import Task from "../models/Task.js";


// GET ALL TASKS
export const getTasks = async (req, res, next) => {

    try {

        const tasks = await Task.getAll();

        res.status(200).json({
            success: true,
            count: tasks.length,
            data: tasks
        });

    } catch (error) {

        next(error);

    }
};


// GET TASK BY ID
export const getTaskById = async (req, res, next) => {

    try {

        const { id } = req.params;

        const task = await Task.getById(id);

        if (!task) {

            return res.status(404).json({
                success: false,
                message: "Task not found"
            });

        }

        res.status(200).json({
            success: true,
            data: task
        });

    } catch (error) {

        next(error);

    }
};


// CREATE TASK
export const createTask = async (req, res, next) => {

    try {

        const { Detail, emp_id } = req.body;

        const task = await Task.create(
            Detail,
            emp_id
        );

        res.status(201).json({
            success: true,
            message: "Task created successfully",
            data: task
        });

    } catch (error) {

        next(error);

    }
};


// UPDATE TASK
export const updateTask = async (req, res, next) => {

    try {

        const { id } = req.params;

        const { Detail, emp_id } = req.body;

        const task = await Task.update(
            id,
            Detail,
            emp_id
        );

        if (!task) {

            return res.status(404).json({
                success: false,
                message: "Task not found"
            });

        }

        res.status(200).json({
            success: true,
            message: "Task updated successfully",
            data: task
        });

    } catch (error) {

        next(error);

    }
};


// DELETE TASK
export const deleteTask = async (req, res, next) => {

    try {

        const { id } = req.params;

        const deleted = await Task.delete(id);

        if (!deleted) {

            return res.status(404).json({
                success: false,
                message: "Task not found"
            });

        }

        res.status(200).json({
            success: true,
            message: "Task deleted successfully"
        });

    } catch (error) {

        next(error);

    }
};