// ===============================================================
//
// FILE NAME : database.js
//
// PURPOSE
// --------
// Ye file MySQL Database se connection banati hai.
//
// Is file ko project me sirf EK BAAR banaya jata hai.
//
// Baad me sab Models isi connection ko use karte hain.
//
// ===============================================================


// mysql2 package import
import mysql from "mysql2/promise";

// dotenv package import
import dotenv from "dotenv";

// .env file load karega
dotenv.config();


// ===============================================================
//
// Create Connection Pool
//
// ===============================================================

const pool = mysql.createPool({

    host: process.env.DB_HOST,

    user: process.env.DB_USER,

    password: process.env.DB_PASSWORD,

    database: process.env.DB_NAME,

    waitForConnections: true,

    connectionLimit: 10,

    queueLimit: 0

});


// ===============================================================
//
// Export Pool
//
// ===============================================================

export default pool;