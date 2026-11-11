import pool from "../config/database.js";

export const getAllFaqs = async () => {

    const [rows] = await pool.query(

        `SELECT
            f.id,
            f.question,
            f.answer,
            f.sort_order,
            f.status,
            f.created_at,
            sc.name AS category

        FROM faqs f

        LEFT JOIN support_categories sc

        ON f.category_id = sc.id

        ORDER BY f.sort_order ASC`

    );

    return rows;

};

export const getFaqById = async (id) => {

    const [rows] = await pool.query(

        `SELECT *

        FROM faqs

        WHERE id=?`,

        [id]

    );

    return rows[0];

};

export const createFaq = async (data) => {

    const {

        category_id,
        question,
        answer,
        sort_order,
        status

    } = data;

    const [result] = await pool.query(

        `INSERT INTO faqs

        (
            category_id,
            question,
            answer,
            sort_order,
            status
        )

        VALUES

        (
            ?,
            ?,
            ?,
            ?,
            ?
        )`,

        [

            category_id,
            question,
            answer,
            sort_order,
            status

        ]

    );

    return result;

};

export const updateFaq = async (id, data) => {

    const {

        category_id,
        question,
        answer,
        sort_order,
        status

    } = data;

    const [result] = await pool.query(

        `UPDATE faqs

        SET

            category_id=?,
            question=?,
            answer=?,
            sort_order=?,
            status=?

        WHERE id=?`,

        [

            category_id,
            question,
            answer,
            sort_order,
            status,
            id

        ]

    );

    return result;

};

export const deleteFaq = async (id) => {

    const [result] = await pool.query(

        `DELETE FROM faqs

        WHERE id=?`,

        [id]

    );

    return result;

};