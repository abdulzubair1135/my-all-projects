// ==========================================================
//
// JWT HELPER
//
// ==========================================================

import jwt from "jsonwebtoken";

// Generate Token

export const generateToken = (user) => {

    return jwt.sign(

        {

            id: user.id,

            email: user.email,

            role: user.role

        },

        process.env.JWT_SECRET,

        {

            expiresIn: "7d"

        }

    );

};

// Verify Token

export const verifyToken = (token) => {

    return jwt.verify(

        token,

        process.env.JWT_SECRET

    );

};