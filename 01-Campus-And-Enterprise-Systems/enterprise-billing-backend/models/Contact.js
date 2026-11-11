import pool from "../config/database.js";

/*
|--------------------------------------------------------------------------
| Get All Contacts
|--------------------------------------------------------------------------
*/
export const getAllContacts = async () => {

    const [rows] = await pool.query(
        "SELECT * FROM contacts ORDER BY id DESC"
    );

    return rows;
};

/*
|--------------------------------------------------------------------------
| Get Contact By ID
|--------------------------------------------------------------------------
*/
export const getContact = async (id) => {

    const [rows] = await pool.query(
        "SELECT * FROM contacts WHERE id=?",
        [id]
    );

    return rows[0];
};

/*
|--------------------------------------------------------------------------
| Create Contact
|--------------------------------------------------------------------------
*/
export const createContact = async (data) => {

    const {
        name,
        email,
        phone,
        subject,
        message
    } = data;

    const [result] = await pool.query(
        `INSERT INTO contacts
        (name,email,phone,subject,message)
        VALUES (?,?,?,?,?)`,
        [
            name,
            email,
            phone,
            subject,
            message
        ]
    );

    return result;
};

/*
|--------------------------------------------------------------------------
| Delete Contact
|--------------------------------------------------------------------------
*/
export const deleteContact = async (id) => {

    const [result] = await pool.query(
        "DELETE FROM contacts WHERE id=?",
        [id]
    );

    return result;
};