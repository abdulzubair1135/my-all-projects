// ==========================================================
//
// FILE : create.controller.js
//
// PURPOSE
// --------
// Database me naya record insert karna.
//
// Example:
//
// POST /users
// POST /services
// POST /plans
//
// ==========================================================

import User from "../models/User.js";

class UserController {

    async create(req, res) {

        try {

            const id = await User.create(

                req.body

            );

            res.status(201).json({

                success: true,

                message: "User Created Successfully",

                id

            });

        }

        catch (err) {

            res.status(500).json({

                success: false,

                message: err.message

            });

        }

    }

}

export default new UserController();