// =====================================================================
//
// FILE NAME : server.js
//
// PURPOSE
// -------
// Ye project ki Main File hai.
//
// Sabse pehle ye file run hoti hai.
//
// Ye Express Server start karti hai.
//
// Is file me:
//
// ✔ Express
// ✔ Middleware
// ✔ Routes
// ✔ Database
// ✔ Server
//
// sab connect hote hain.
//
// =====================================================================


// ================================
// Imports
// ================================

import express from "express";

import dotenv from "dotenv";

import cors from "cors";

import helmet from "helmet";

import morgan from "morgan";


// ================================
// Load Environment Variables
// ================================

dotenv.config();


// ================================
// Create Express App
// ================================

const app = express();


// ================================
// Middlewares
// ================================

// JSON Read karega
app.use(express.json());

// Form Data Read karega
app.use(express.urlencoded({ extended: true }));

// Security
app.use(helmet());

// Cross Origin
app.use(cors());

// Console Logs
app.use(morgan("dev"));


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
// Start Server
// ================================

const PORT = process.env.PORT || 5000;

app.listen(PORT, () => {

    console.log(

        `Server Running On Port ${PORT}`

    );

});