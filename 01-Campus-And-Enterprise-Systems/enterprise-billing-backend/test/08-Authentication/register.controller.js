import User from "../models/User.js";

import {

    hashPassword

} from "../helpers/password.helper.js";

class RegisterController {

    async register(req, res) {

        try {

            const data = req.body;

            // Hash Password

            data.password =

                await hashPassword(

                    data.password

                );

            // Save

            const id =

                await User.create(data);

            res.status(201).json({

                success: true,

                message: "Registration Successful",

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

export default new RegisterController();