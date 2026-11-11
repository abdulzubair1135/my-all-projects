import pool from "../config/database.js";

// Fetch overview metrics for the main control panel screen (Admin)
export const getDashboard = async (req, res) => {
    try {
        // 1. Leads/Enquiries Stats
        const [[{ totalLeads }]] = await pool.query("SELECT COUNT(*) AS totalLeads FROM leads");
        const [[{ openLeads }]] = await pool.query("SELECT COUNT(*) AS openLeads FROM leads WHERE status = 'new'");
        const [[{ todayLeads }]] = await pool.query("SELECT COUNT(*) AS todayLeads FROM leads WHERE DATE(created_at) = CURDATE()");
        
        // Leads count grouped by status
        const statuses = ["new", "contacted", "in_progress", "resolved", "spam"];
        const byStatus = [];
        for (let status of statuses) {
            const [[{ count }]] = await pool.query("SELECT COUNT(*) AS count FROM leads WHERE status = ?", [status]);
            byStatus.push({ status, count });
        }

        // 2. DishTV packages count
        const [[{ activeDish }]] = await pool.query("SELECT COUNT(*) AS count FROM dish_packages WHERE is_active = 1");
        const [[{ totalDish }]] = await pool.query("SELECT COUNT(*) AS count FROM dish_packages");

        // 3. OTT Packages count
        const [[{ activeOtt }]] = await pool.query("SELECT COUNT(*) AS count FROM ott_packages WHERE is_active = 1");
        const [[{ totalOtt }]] = await pool.query("SELECT COUNT(*) AS count FROM ott_packages");

        // 4. Content Blocks count
        const [[{ totalBlocks }]] = await pool.query("SELECT COUNT(*) AS count FROM content_blocks");
        const [[{ publishedBlocks }]] = await pool.query("SELECT COUNT(*) AS count FROM content_blocks WHERE is_published = 1");

        // 5. Fetch 5 most recent leads
        const [recentLeadsRows] = await pool.query("SELECT * FROM leads ORDER BY id DESC LIMIT 5");

        return res.status(200).json({
            success: true,
            data: {
                leads: {
                    total: totalLeads,
                    open: openLeads,
                    today: todayLeads,
                    byStatus
                },
                activeDishPackages: activeDish,
                totalDishPackages: totalDish,
                activeOttPackages: activeOtt,
                totalOttPackages: totalOtt,
                totalContentBlocks: totalBlocks,
                publishedContentBlocks: publishedBlocks,
                recentLeads: recentLeadsRows
            }
        });

    } catch (err) {
        return res.status(500).json({
            success: false,
            message: err.message
        });
    }
};