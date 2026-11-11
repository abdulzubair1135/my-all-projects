// =====================================================================
//
// FILE NAME : server.js
//
// PURPOSE
// -------
// Ye project ki Main File hai.
//
// =====================================================================

import express from "express";
import dotenv from "dotenv";

// Routes
import authRoutes from "./routes/auth.routes.js";
import userRoutes from "./routes/user.routes.js";
import tasksRoutes from "./routes/task.routes.js";

// Load Environment Variables
dotenv.config();

// Create Express App
const app = express();

// ================================
// Middlewares
// ================================

app.use(express.json());

app.use(express.urlencoded({ extended: true }));

// ================================
// Test Route
// ================================

app.get("/", (req, res) => {

    res.json({
        success: true,
        message: "Backend Running Successfully"
    });

});

// ================================
// API Routes
// ================================

app.use("/api/auth", authRoutes);

app.use("/api/users", userRoutes);

app.use("/api/tasks", tasksRoutes);

// ================================
// Start Server
// ================================

const PORT = process.env.PORT || 5000;

app.listen(PORT, () => {

    console.log(`Server Running On Port ${PORT}`);

});