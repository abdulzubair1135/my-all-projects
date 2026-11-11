import pool from "../config/database.js";

class Dashboard {

    static async getStats() {

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
            totalUsers: users.totalUsers,
            totalServices: services.totalServices,
            totalPlans: plans.totalPlans,
            totalContacts: contacts.totalContacts
        };

    }

}

export default Dashboard;