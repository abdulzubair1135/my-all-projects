import bcrypt from "bcrypt";
import jwt from "jsonwebtoken";
import * as Admin from "../models/Admin.js";

// Admin login action
export const login = async (req, res) => {
    try {
        const { email, password } = req.body;

        if (!email || !password) {
            return res.status(400).json({
                success: false,
                message: "Email and Password Required"
            });
        }

        const admin = await Admin.findByEmail(email);

        if (!admin) {
            return res.status(401).json({
                success: false,
                message: "Invalid Credentials"
            });
        }

        const valid = await bcrypt.compare(password, admin.password);

        if (!valid) {
            return res.status(401).json({
                success: false,
                message: "Invalid Credentials"
            });
        }

        await Admin.updateLastLogin(admin.id);

        const token = jwt.sign(
            {
                id: admin.id,
                email: admin.email,
                role: admin.role || "admin"
            },
            process.env.JWT_SECRET,
            {
                expiresIn: process.env.JWT_EXPIRES_IN || "7d"
            }
        );

        // Return login success with data format expected by React client
        return res.json({
            success: true,
            data: {
                accessToken: token,
                user: {
                    id: admin.id,
                    name: admin.name,
                    email: admin.email,
                    role: admin.role || "admin"
                }
            }
        });

    } catch (err) {
        return res.status(500).json({
            success: false,
            message: err.message
        });
    }
};

// Fetch current user details (using token)
export const me = async (req, res) => {
    try {
        const admin = await Admin.findById(req.user.id);
        if (!admin) {
            return res.status(404).json({
                success: false,
                message: "User not found"
            });
        }

        return res.json({
            success: true,
            data: {
                id: admin.id,
                name: admin.name,
                email: admin.email,
                role: admin.role || "admin"
            }
        });
    } catch (err) {
        return res.status(500).json({
            success: false,
            message: err.message
        });
    }
};

// Refresh token renewal action
export const refresh = async (req, res) => {
    try {
        const header = req.headers.authorization;
        if (!header) {
            return res.status(401).json({
                success: false,
                message: "No token provided"
            });
        }

        const token = header.split(" ")[1];

        // Decode even if expired
        const decoded = jwt.verify(token, process.env.JWT_SECRET, { ignoreExpiration: true });

        // Sign new token
        const newToken = jwt.sign(
            {
                id: decoded.id,
                email: decoded.email,
                role: decoded.role || "admin"
            },
            process.env.JWT_SECRET,
            {
                expiresIn: process.env.JWT_EXPIRES_IN || "7d"
            }
        );

        return res.json({
            success: true,
            data: {
                accessToken: newToken
            }
        });
    } catch (err) {
        return res.status(401).json({
            success: false,
            message: "Invalid token"
        });
    }
};

// Logout session clear action
export const logout = async (req, res) => {
    return res.json({
        success: true,
        message: "Logged out successfully"
    });
};