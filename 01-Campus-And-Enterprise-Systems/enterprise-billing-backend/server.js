import express from "express";
import dotenv from "dotenv";
import cors from "cors";
import helmet from "helmet";
import morgan from "morgan";
import cookieParser from "cookie-parser";
import path from "path";
import { fileURLToPath } from "url";

import pool from "./config/database.js";
import limiter from "./middleware/rateLimiter.js";

// Routes Imports
import authRoutes from "./routes/auth.routes.js";
import userRoutes from "./routes/user.routes.js";
import dashboardRoutes from "./routes/dashboard.routes.js";
import leadsRoutes from "./routes/leads.routes.js";
import dishPackagesRoutes from "./routes/dishPackages.routes.js";
import channelsRoutes from "./routes/channels.routes.js";
import ottRoutes from "./routes/ott.routes.js";
import contentBlocksRoutes from "./routes/contentBlocks.routes.js";
import ordersRoutes from "./routes/orders.routes.js";
import mediaRoutes from "./routes/media.routes.js";
import auditLogsRoutes from "./routes/auditLogs.routes.js";
import reportsRoutes from "./routes/reports.routes.js";

dotenv.config();

const app = express();

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Middlewares
app.use(cors());

// Configure helmet loosely for local static site rendering
app.use(
    helmet({
        contentSecurityPolicy: false,
        crossOriginEmbedderPolicy: false
    })
);

app.use(morgan("dev"));
app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(cookieParser());

// Static folders
app.use("/uploads", express.static(path.join(__dirname, "uploads")));
app.use(express.static(path.join(__dirname, "wss/wssbhuj.in")));

// Base API health test route
app.get("/api/health", (req, res) => {
    res.json({
        success: true,
        status: "OK",
        uptime: process.uptime(),
        timestamp: new Date()
    });
});

// Database connection test route
app.get("/api/db-test", async (req, res) => {
    try {
        const conn = await pool.getConnection();
        conn.release();
        res.json({
            success: true,
            database: "Connected"
        });
    } catch (err) {
        res.status(500).json({
            success: false,
            message: "Database Connection Failed",
            error: err.message
        });
    }
});

// Rate limiter for API routes
app.use("/api/", limiter);

// Register API Routes
app.use("/api/auth", authRoutes);
app.use("/api/users", userRoutes);
app.use("/api/dashboard", dashboardRoutes);
app.use("/api/leads", leadsRoutes);
app.use("/api/dish-packages", dishPackagesRoutes);
app.use("/api/channels", channelsRoutes);
app.use("/api/sales-catalogue", ottRoutes);
app.use("/api/content-blocks", contentBlocksRoutes);
app.use("/api/orders", ordersRoutes);
app.use("/api/media", mediaRoutes);
app.use("/api/audit-logs", auditLogsRoutes);
app.use("/api/reports", reportsRoutes);

// Fallback client-side routing fallback for React SPA
app.get("*all", (req, res) => {
    if (!req.url.startsWith("/api/")) {
        res.sendFile(path.join(__dirname, "wss/wssbhuj.in/index.html"));
    } else {
        res.status(404).json({
            success: false,
            message: "API Route Not Found"
        });
    }
});

// Start Server
const PORT = process.env.PORT || 5000;
app.listen(PORT, () => {
    console.log("");
    console.log("=========================================");
    console.log(`🚀 WSS Hub Full Stack Server Running`);
    console.log(`🌐 Local Website: http://localhost:${PORT}`);
    console.log(`📊 Admin Panel  : http://localhost:${PORT}/admin`);
    console.log("=========================================");
});