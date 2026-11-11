import pool from "../config/database.js";

/*
|--------------------------------------------------------------------------
| Dashboard Analytics
|--------------------------------------------------------------------------
*/

export const getAnalytics = async () => {

    const [[users]] = await pool.query(
        "SELECT COUNT(*) AS totalUsers FROM users"
    );

    const [[services]] = await pool.query(
        "SELECT COUNT(*) AS totalServices FROM services"
    );

    const [[plans]] = await pool.query(
        "SELECT COUNT(*) AS totalPlans FROM plans"
    );

    const [[contacts]] = await pool.query(
        "SELECT COUNT(*) AS totalContacts FROM contacts"
    );

    return {
        users: users.totalUsers,
        services: services.totalServices,
        plans: plans.totalPlans,
        contacts: contacts.totalContacts
    };

};