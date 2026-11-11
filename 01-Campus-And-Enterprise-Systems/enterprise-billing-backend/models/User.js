import pool from "../config/database.js";
import bcrypt from "bcrypt";

// GET ALL USERS
export const getAllUsers = async () => {
    const [rows] = await pool.query(
        `SELECT id,name,email,phone,created_at
         FROM users
         ORDER BY id DESC`
    );
    return rows;
};

// GET SINGLE USER
export const getUserById = async (id) => {
    const [rows] = await pool.query(
        `SELECT id,name,email,phone,created_at
         FROM users
         WHERE id=?`,
        [id]
    );

    return rows[0];
};

// CHECK EMAIL
export const findByEmail = async (email) => {

    const [rows] = await pool.query(
        "SELECT * FROM users WHERE email=?",
        [email]
    );

    return rows[0];

};

// CREATE USER
export const createUser = async (data) => {

    const { name, email, phone, password } = data;

    const exists = await findByEmail(email);

    if (exists) {
        throw new Error("Email already exists");
    }

    const hash = await bcrypt.hash(password, 10);

    const [result] = await pool.query(

        `INSERT INTO users
        (name,email,phone,password)
        VALUES(?,?,?,?)`,

        [name, email, phone, hash]

    );

    return result;

};

// UPDATE USER
export const updateUser = async (id, data) => {

    const { name, email, phone } = data;

    const [result] = await pool.query(

        `UPDATE users
        SET
        name=?,
        email=?,
        phone=?
        WHERE id=?`,

        [name, email, phone, id]

    );

    return result;

};

// DELETE USER
export const deleteUser = async (id) => {

    const [result] = await pool.query(
        "DELETE FROM users WHERE id=?",
        [id]
    );

    return result;

};