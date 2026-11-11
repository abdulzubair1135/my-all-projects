import pool from "../config/database.js";

/*
|--------------------------------------------------------------------------
| OTT Apps Queries
|--------------------------------------------------------------------------
*/

export const getAllApps = async () => {
    const [rows] = await pool.query("SELECT * FROM ott_apps ORDER BY sort_order ASC, name ASC");
    return rows.map(app => ({
        id: app.id,
        name: app.name,
        slug: app.slug,
        logo_file: app.logo_file,
        is_active: !!app.is_active,
        sort_order: app.sort_order
    }));
};

export const getAppById = async (id) => {
    const [rows] = await pool.query("SELECT * FROM ott_apps WHERE id = ? LIMIT 1", [id]);
    return rows[0];
};

export const createApp = async (data) => {
    const { name, slug, logoFile, isActive, sortOrder } = data;
    const [result] = await pool.query(
        "INSERT INTO ott_apps (name, slug, logo_file, is_active, sort_order) VALUES (?, ?, ?, ?, ?)",
        [name, slug, logoFile, isActive ? 1 : 0, sortOrder || 0]
    );
    return result;
};

export const updateApp = async (id, data) => {
    const { name, slug, logoFile, isActive, sortOrder } = data;
    const [result] = await pool.query(
        `UPDATE ott_apps 
         SET name = ?, slug = ?, logo_file = ?, is_active = ?, sort_order = ? 
         WHERE id = ?`,
        [name, slug, logoFile, isActive ? 1 : 0, sortOrder || 0, id]
    );
    return result;
};

export const deleteApp = async (id) => {
    // Delete many-to-many associations first
    await pool.query("DELETE FROM ott_package_apps WHERE app_id = ?", [id]);
    const [result] = await pool.query("DELETE FROM ott_apps WHERE id = ?", [id]);
    return result;
};


/*
|--------------------------------------------------------------------------
| OTT Packages Queries
|--------------------------------------------------------------------------
*/

export const getAllPackages = async () => {
    const [packages] = await pool.query("SELECT * FROM ott_packages ORDER BY sort_order ASC, name ASC");

    for (let pkg of packages) {
        // Fetch apps
        const [apps] = await pool.query(
            `SELECT a.* FROM ott_apps a 
             JOIN ott_package_apps opa ON a.id = opa.app_id
             WHERE opa.package_id = ?`,
            [pkg.id]
        );
        pkg.apps = apps.map(app => ({
            id: app.id,
            name: app.name,
            logo_file: app.logo_file,
            is_active: !!app.is_active,
            sort_order: app.sort_order
        }));

        // Fetch prices
        const [priceRows] = await pool.query(
            "SELECT months, price, playbox_pack_code FROM ott_package_prices WHERE package_id = ?",
            [pkg.id]
        );
        
        const prices = {};
        const playboxPackCodes = {};
        
        priceRows.forEach(pr => {
            prices[pr.months] = Number(pr.price);
            playboxPackCodes[pr.months] = pr.playbox_pack_code || "";
        });
        
        pkg.prices = prices;
        pkg.playboxPackCodes = playboxPackCodes;
        pkg.is_popular = !!pkg.is_popular;
        pkg.is_active = !!pkg.is_active;
    }

    return packages;
};

export const getPackageById = async (id) => {
    const [rows] = await pool.query("SELECT * FROM ott_packages WHERE id = ? LIMIT 1", [id]);
    if (rows.length === 0) return null;

    const pkg = rows[0];

    // Fetch app IDs
    const [appRows] = await pool.query("SELECT app_id FROM ott_package_apps WHERE package_id = ?", [id]);
    pkg.appIds = appRows.map(r => r.app_id);

    // Fetch prices
    const [priceRows] = await pool.query(
        "SELECT months, price, playbox_pack_code FROM ott_package_prices WHERE package_id = ?",
        [id]
    );

    const prices = {};
    const playboxPackCodes = {};
    priceRows.forEach(pr => {
        prices[pr.months] = Number(pr.price);
        playboxPackCodes[pr.months] = pr.playbox_pack_code || "";
    });

    pkg.prices = prices;
    pkg.playboxPackCodes = playboxPackCodes;
    pkg.is_popular = !!pkg.is_popular;
    pkg.is_active = !!pkg.is_active;

    return pkg;
};

export const createPackage = async (data) => {
    const { name, slug, eyebrow, accent, tint, isPopular, isActive, sortOrder, appIds = [], prices = [] } = data;

    const [result] = await pool.query(
        `INSERT INTO ott_packages (name, slug, eyebrow, accent, tint, is_popular, is_active, sort_order) 
         VALUES (?, ?, ?, ?, ?, ?, ?, ?)`,
        [name, slug, eyebrow, accent, tint, isPopular ? 1 : 0, isActive ? 1 : 0, sortOrder || 0]
    );

    const packageId = result.insertId;

    // Save app mappings
    if (appIds.length > 0) {
        const values = appIds.map(appId => [packageId, appId]);
        await pool.query("INSERT INTO ott_package_apps (package_id, app_id) VALUES ?", [values]);
    }

    // Save prices
    if (prices.length > 0) {
        for (let priceObj of prices) {
            await pool.query(
                "INSERT INTO ott_package_prices (package_id, months, price, playbox_pack_code) VALUES (?, ?, ?, ?)",
                [packageId, priceObj.months, priceObj.price, priceObj.playboxPackCode || null]
            );
        }
    }

    return result;
};

export const updatePackage = async (id, data) => {
    const { name, slug, eyebrow, accent, tint, isPopular, isActive, sortOrder, appIds = [], prices = [] } = data;

    const [result] = await pool.query(
        `UPDATE ott_packages 
         SET name = ?, slug = ?, eyebrow = ?, accent = ?, tint = ?, is_popular = ?, is_active = ?, sort_order = ? 
         WHERE id = ?`,
        [name, slug, eyebrow, accent, tint, isPopular ? 1 : 0, isActive ? 1 : 0, sortOrder || 0, id]
    );

    // Update app associations
    await pool.query("DELETE FROM ott_package_apps WHERE package_id = ?", [id]);
    if (appIds.length > 0) {
        const values = appIds.map(appId => [id, appId]);
        await pool.query("INSERT INTO ott_package_apps (package_id, app_id) VALUES ?", [values]);
    }

    // Update prices
    await pool.query("DELETE FROM ott_package_prices WHERE package_id = ?", [id]);
    if (prices.length > 0) {
        for (let priceObj of prices) {
            await pool.query(
                "INSERT INTO ott_package_prices (package_id, months, price, playbox_pack_code) VALUES (?, ?, ?, ?)",
                [id, priceObj.months, priceObj.price, priceObj.playboxPackCode || null]
            );
        }
    }

    return result;
};

export const deletePackage = async (id) => {
    await pool.query("DELETE FROM ott_package_apps WHERE package_id = ?", [id]);
    await pool.query("DELETE FROM ott_package_prices WHERE package_id = ?", [id]);
    const [result] = await pool.query("DELETE FROM ott_packages WHERE id = ?", [id]);
    return result;
};


/*
|--------------------------------------------------------------------------
| Dish Billing Terms Queries
|--------------------------------------------------------------------------
*/

export const getAllBillingTerms = async () => {
    const [rows] = await pool.query("SELECT * FROM dish_billing_terms ORDER BY sort_order ASC, months ASC");
    return rows;
};

export const getBillingTermById = async (id) => {
    const [rows] = await pool.query("SELECT * FROM dish_billing_terms WHERE id = ? LIMIT 1", [id]);
    return rows[0];
};

export const createBillingTerm = async (data) => {
    const { months, installationPrice, savingAmount, sortOrder } = data;
    const [result] = await pool.query(
        "INSERT INTO dish_billing_terms (months, installation_price, saving_amount, sort_order) VALUES (?, ?, ?, ?)",
        [months, installationPrice, savingAmount, sortOrder || 0]
    );
    return result;
};

export const updateBillingTerm = async (id, data) => {
    const { months, installationPrice, savingAmount, sortOrder } = data;
    const [result] = await pool.query(
        `UPDATE dish_billing_terms 
         SET months = ?, installation_price = ?, saving_amount = ?, sort_order = ? 
         WHERE id = ?`,
        [months, installationPrice, savingAmount, sortOrder || 0, id]
    );
    return result;
};

export const deleteBillingTerm = async (id) => {
    const [result] = await pool.query("DELETE FROM dish_billing_terms WHERE id = ?", [id]);
    return result;
};
