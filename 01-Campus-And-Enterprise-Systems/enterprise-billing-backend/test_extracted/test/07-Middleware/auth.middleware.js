// =============================================================
//
// FILE : auth.middleware.js
//
// PURPOSE
// --------
//
// JWT Token Verify Karna
//
// Protected APIs ke liye
//
// =============================================================

import jwt from "jsonwebtoken";

const auth = (req, res, next) => {

    try {

        // Authorization Header

        const header = req.headers.authorization;

        // Token Check

        if (!header) {

            return res.status(401).json({

                success: false,

                message: "Token Missing"

            });

        }

        // Remove Bearer

        const token = header.split(" ")[1];

        // Verify Token

        const decoded = jwt.verify(

            token,

            process.env.JWT_SECRET

        );

        // Save User

        req.user = decoded;

        // Next Middleware

        next();

    }

    catch (err) {

        res.status(401).json({

            success: false,

            message: "Invalid Token"

        });

    }

};

export default auth;