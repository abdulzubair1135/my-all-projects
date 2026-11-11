// ==========================================================
//
// FILE : delete.controller.js
//
// PURPOSE
// --------
// Database se Record Delete Karna.
//
// Example:
//
// DELETE /users/5
//
// ==========================================================

import User from "../models/User.js";

class UserController {

    // ======================================================
    // DELETE USER
    //
    // URL
    // DELETE /users/:id
    //
    // ======================================================

    async delete(req, res) {

        try {

            const result = await User.delete(

                req.params.id

            );

            // =============================================
            // Record Exist Nahi
            // =============================================

            if (result.affectedRows === 0) {

                return res.status(404).json({

                    success: false,

                    message: "User Not Found"

                });

            }

            // =============================================
            // Success
            // =============================================

            res.status(200).json({

                success: true,

                message: "User Deleted Successfully"

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