// ============================================================
// FILE NAME : user.controller.js
// PURPOSE   : User API Controllers
// ============================================================

import User from "../models/User.js";


// ============================================================
// GET ALL USERS
// GET /api/users
// ============================================================

export const getUsers = async (req, res, next) => {

    try {

        const users = await User.getAllUsers();

        return res.status(200).json({

            success: true,

            users

        });

    } catch (error) {

        console.error("GET USERS ERROR:", error);

        next(error);

    }

};


// ============================================================
// GET USER BY ID
// GET /api/users/:id
// ============================================================

export const getUserById = async (req, res, next) => {

    try {

        const { id } = req.params;

        const user = await User.getUserById(id);


        if (!user) {

            return res.status(404).json({

                success: false,

                message: "User not found"

            });

        }


        return res.status(200).json({

            success: true,

            user

        });

    } catch (error) {

        console.error("GET USER ERROR:", error);

        next(error);

    }

};