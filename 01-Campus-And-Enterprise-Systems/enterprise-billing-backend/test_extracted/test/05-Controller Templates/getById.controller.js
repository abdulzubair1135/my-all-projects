// ==========================================================
//
// FILE : getById.controller.js
//
// PURPOSE
// --------
// Database se sirf EK Record lana.
//
// Example:
//
// GET /users/5
// GET /services/10
// GET /plans/3
//
// ==========================================================

import User from "../models/User.js";

class UserController {

    // =====================================================
    // GET USER BY ID
    //
    // URL :
    // /users/:id
    //
    // Method :
    // GET
    //
    // Parameter :
    // req.params.id
    //
    // =====================================================

    async getById(req, res) {

        try {

            const user = await User.getById(

                req.params.id

            );

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