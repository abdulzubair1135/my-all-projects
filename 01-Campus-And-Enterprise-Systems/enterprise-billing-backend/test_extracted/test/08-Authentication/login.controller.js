import User from "../models/User.js";

import {

    comparePassword

} from "../helpers/password.helper.js";

import {

    generateToken

} from "../helpers/jwt.helper.js";

class LoginController {

    async login(req, res) {

        try {

            const {

                email,

                password

            } = req.body;

            // Find User

            const user =

                await User.findByEmail(email);

            if (!user) {

                return res.status(404).json({

                    success: false,

                    message: "User Not Found"

                });

            }

            // Compare Password

            const match =

                await comparePassword(

                    password,

                    user.password

                );

            if (!match) {

                return res.status(401).json({

                    success: false,

                    message: "Invalid Password"

                });

            }

            // Generate Token

            const token =

                generateToken(user);

            // Response

            res.status(200).json({

                success: true,

                token

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

export default new LoginController();