import bcrypt from "bcrypt";
import jwt from "jsonwebtoken";

import User from "../models/User.js";


export const login = async (req, res, next) => {

    try {

        // =========================================
        // 1. Request body se email/password lena
        // =========================================

        const { email, password } = req.body;


        // =========================================
        // 2. Validation
        // =========================================

        if (!email || !password) {

            return res.status(400).json({

                success: false,

                message: "Email and password are required"

            });

        }


        // =========================================
        // 3. Database se user find karna
        // =========================================

        const user = await User.findUserByEmail(email);


        console.log("========== LOGIN DEBUG ==========");
        console.log("LOGIN EMAIL:", email);
        console.log("USER FOUND:", !!user);


        if (user) {

            console.log("USER ID:", user.id);
            console.log("USER EMAIL:", user.email);
            console.log("HASH EXISTS:", !!user.password);
            console.log("HASH LENGTH:", user.password?.length);

        }


        console.log("=================================");


        // =========================================
        // 4. User nahi mila
        // =========================================

        if (!user) {

            return res.status(401).json({

                success: false,

                message: "Invalid email or password"

            });

        }


        // =========================================
        // 5. Password verify
        // =========================================

        const isMatch = await bcrypt.compare(

            password,

            user.password

        );


        console.log("PASSWORD MATCH:", isMatch);


        // =========================================
        // 6. Password wrong
        // =========================================

        if (!isMatch) {

            return res.status(401).json({

                success: false,

                message: "Invalid email or password"

            });

        }


        // =========================================
        // 7. JWT Token generate
        // =========================================

        const token = jwt.sign(

            {
                id: user.id,

                email: user.email
            },

            process.env.JWT_SECRET,

            {
                expiresIn: process.env.JWT_EXPIRES_IN || "1d"
            }

        );


        // =========================================
        // 8. Success response
        // =========================================

        return res.status(200).json({

            success: true,

            message: "Login successful",

            token

        });


    } catch (error) {

        console.error("LOGIN ERROR:", error);

        next(error);

    }

};