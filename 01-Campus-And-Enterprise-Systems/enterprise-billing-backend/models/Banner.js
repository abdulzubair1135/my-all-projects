import pool from "../config/database.js";

/*
|--------------------------------------------------------------------------
| Get All Banners
|--------------------------------------------------------------------------
*/
export const getAllBanners = async () => {

    const [rows] = await pool.query(
        "SELECT * FROM banners ORDER BY id DESC"
    );

    return rows;
};

/*
|--------------------------------------------------------------------------
| Get Banner By ID
|--------------------------------------------------------------------------
*/
export const getBanner = async (id) => {

    const [rows] = await pool.query(
        "SELECT * FROM banners WHERE id=?",
        [id]
    );

    return rows[0];
};

/*
|--------------------------------------------------------------------------
| Create Banner
|--------------------------------------------------------------------------
*/
export const createBanner = async (data) => {

    const {
        title,
        subtitle,
        image
    } = data;

    const [result] = await pool.query(
        `INSERT INTO banners
        (title, subtitle, image)
        VALUES (?, ?, ?)`,
        [
            title,
            subtitle,
            image
        ]
    );

    return result;
};

/*
|--------------------------------------------------------------------------
| Update Banner
|--------------------------------------------------------------------------
*/
export const updateBanner = async (id, data) => {

    const {
        title,
        subtitle,
        image
    } = data;

    const [result] = await pool.query(
        `UPDATE banners
        SET
        title=?,
        subtitle=?,
        image=?
        WHERE id=?`,
        [
            title,
            subtitle,
            image,
            id
        ]
    );

    return result;
};

/*
|--------------------------------------------------------------------------
| Delete Banner
|--------------------------------------------------------------------------
*/
export const deleteBanner = async (id) => {

    const [result] = await pool.query(
        "DELETE FROM banners WHERE id=?",
        [id]
    );

    return result;
};