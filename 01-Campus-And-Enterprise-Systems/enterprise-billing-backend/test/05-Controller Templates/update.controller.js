// ==========================================================
//
// FILE : update.controller.js
//
// PURPOSE
// --------
// Existing Record Update Karna.
//
// Example:
//
// PUT /users/5
// PUT /services/10
//
// ==========================================================

import User from "../models/User.js";

class UserController {

    // ======================================================
    // UPDATE USER
    //
    // URL:
    // PUT /users/:id
    //
    // req.params.id
    // req.body
    //
    // ======================================================

    async update(req, res) {

        try {

            const result = await User.update(

                req.params.id,

                req.body

            );

            // =============================================
            // Record Exist Nahi Karta
            // =============================================

            if (result.affectedRows === 0) {

                return res.status(404).json({

                    success: false,

                    message: "User Not Found"

                });

            }

            // =============================================
            // Success Response
            // =============================================

            res.status(200).json({

                success: true,

                message: "User Updated Successfully"

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