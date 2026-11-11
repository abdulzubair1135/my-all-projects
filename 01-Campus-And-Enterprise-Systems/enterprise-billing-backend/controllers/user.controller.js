import * as User from "../models/User.js";

// GET ALL USERS
export const getUsers = async (req, res) => {

    try {

        const users = await User.getAllUsers();

        res.status(200).json({
            success: true,
            count: users.length,
            data: users
        });

    } catch (err) {

        res.status(500).json({
            success: false,
            message: err.message
        });

    }

};

// GET SINGLE USER
export const getUser = async (req, res) => {

    try {

        const user = await User.getUserById(req.params.id);

        if (!user) {

            return res.status(404).json({
                success: false,
                message: "User Not Found"
            });

        }

        res.status(200).json({
            success: true,
            data: user
        });

    } catch (err) {

        res.status(500).json({
            success: false,
            message: err.message
        });

    }

};

// CREATE USER
export const createUser = async (req, res) => {

    try {

        await User.createUser(req.body);

        res.status(201).json({
            success: true,
            message: "User Created Successfully"
        });

    } catch (err) {

        res.status(400).json({
            success: false,
            message: err.message
        });

    }

};

// UPDATE USER
export const updateUser = async (req, res) => {

    try {

        const user = await User.getUserById(req.params.id);

        if (!user) {

            return res.status(404).json({
                success: false,
                message: "User Not Found"
            });

        }

        await User.updateUser(req.params.id, req.body);

        res.status(200).json({
            success: true,
            message: "User Updated Successfully"
        });

    } catch (err) {

        res.status(500).json({
            success: false,
            message: err.message
        });

    }

};

// DELETE USER
export const deleteUser = async (req, res) => {

    try {

        const user = await User.getUserById(req.params.id);

        if (!user) {

            return res.status(404).json({
                success: false,
                message: "User Not Found"
            });

        }

        await User.deleteUser(req.params.id);

        res.status(200).json({
            success: true,
            message: "User Deleted Successfully"
        });

    } catch (err) {

        res.status(500).json({
            success: false,
            message: err.message
        });

    }

};