import pool from "../config/database.js";

// Fetch all dish packages and include the channels details
export const getAllPackages = async () => {
    const [packages] = await pool.query(
        "SELECT * FROM dish_packages ORDER BY sort_order ASC, name ASC"
    );

    // Fetch channel mappings for all packages
    for (let pkg of packages) {
        // Parse features JSON/String array
        try {
            pkg.features = pkg.features ? JSON.parse(pkg.features) : [];
        } catch (e) {
            pkg.features = [];
        }

        // Fetch channel details for this package
        const [channels] = await pool.query(
            `SELECT c.* FROM channels c
             JOIN dish_package_channels dpc ON c.id = dpc.channel_id
             WHERE dpc.package_id = ?`,
            [pkg.id]
        );
        pkg.channels = channels;
    }

    return packages;
};

// Fetch single dish package with its list of channelIds
export const getPackageById = async (id) => {
    const [rows] = await pool.query(
        "SELECT * FROM dish_packages WHERE id = ? LIMIT 1",
        [id]
    );

    if (rows.length === 0) return null;

    const pkg = rows[0];

    // Parse features list
    try {
        pkg.features = pkg.features ? JSON.parse(pkg.features) : [];
    } catch (e) {
        pkg.features = [];
    }

    // Fetch channel IDs attached to this package
    const [channelRows] = await pool.query(
        "SELECT channel_id FROM dish_package_channels WHERE package_id = ?",
        [id]
    );
    pkg.channelIds = channelRows.map(r => r.channel_id);

    return pkg;
};

// Create a new Dish Package and save its channel mappings
export const createPackage = async (data) => {
    const {
        name, slug, packageType, price, billingCycle, description,
        features, pdfFile, includeFta, isPopular, isActive, sortOrder, channelIds = []
    } = data;

    const featuresJSON = JSON.stringify(features || []);

    const [result] = await pool.query(
        `INSERT INTO dish_packages 
        (name, slug, package_type, price, billing_cycle, description, features, pdf_file, include_fta, is_popular, is_active, sort_order)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`,
        [
            name, slug, packageType, price, billingCycle, description,
            featuresJSON, pdfFile, includeFta ? 1 : 0, isPopular ? 1 : 0, isActive ? 1 : 0, sortOrder || 0
        ]
    );

    const packageId = result.insertId;

    // Save channel associations
    if (channelIds.length > 0) {
        const values = channelIds.map(channelId => [packageId, channelId]);
        await pool.query(
            "INSERT INTO dish_package_channels (package_id, channel_id) VALUES ?",
            [values]
        );
    }

    return result;
};

// Update an existing package and its channel mappings
export const updatePackage = async (id, data) => {
    const {
        name, slug, packageType, price, billingCycle, description,
        features, pdfFile, includeFta, isPopular, isActive, sortOrder, channelIds = []
    } = data;

    const featuresJSON = JSON.stringify(features || []);

    const [result] = await pool.query(
        `UPDATE dish_packages
         SET name = ?, slug = ?, package_type = ?, price = ?, billing_cycle = ?, description = ?, features = ?, pdf_file = ?, include_fta = ?, is_popular = ?, is_active = ?, sort_order = ?
         WHERE id = ?`,
        [
            name, slug, packageType, price, billingCycle, description,
            featuresJSON, pdfFile, includeFta ? 1 : 0, isPopular ? 1 : 0, isActive ? 1 : 0, sortOrder || 0, id
        ]
    );

    // Update channel associations (Delete old ones and add new ones)
    await pool.query("DELETE FROM dish_package_channels WHERE package_id = ?", [id]);

    if (channelIds.length > 0) {
        const values = channelIds.map(channelId => [id, channelId]);
        await pool.query(
            "INSERT INTO dish_package_channels (package_id, channel_id) VALUES ?",
            [values]
        );
    }

    return result;
};

// Delete a package and its channel mappings
export const deletePackage = async (id) => {
    // Delete package channels associations first
    await pool.query("DELETE FROM dish_package_channels WHERE package_id = ?", [id]);
    
    // Delete package record
    const [result] = await pool.query("DELETE FROM dish_packages WHERE id = ?", [id]);
    return result;
};
