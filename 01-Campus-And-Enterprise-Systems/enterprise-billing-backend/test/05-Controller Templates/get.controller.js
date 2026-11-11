import User from "../models/User.js";

class UserController {

    // ===============================================
    // GET ALL USERS
    //
    // API
    // GET /users
    //
    // ===============================================

    async getAll(req, res) {

        try {

            const users = await User.getAll();

            res.status(200).json({

                success: true,

                count: users.length,

                data: users

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