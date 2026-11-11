import mysql from "mysql2/promise";
import dotenv from "dotenv";

dotenv.config();

const { DB_HOST, DB_USER, DB_PASSWORD, DB_NAME } = process.env;

const tables = {
  admin: `
    CREATE TABLE IF NOT EXISTS admin (
      id INT AUTO_INCREMENT PRIMARY KEY,
      name VARCHAR(100) DEFAULT NULL,
      email VARCHAR(100) UNIQUE DEFAULT NULL,
      password VARCHAR(255) DEFAULT NULL,
      role VARCHAR(50) DEFAULT 'admin',
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      last_login DATETIME DEFAULT NULL
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
  `,
  leads: `
    CREATE TABLE IF NOT EXISTS leads (
      id INT AUTO_INCREMENT PRIMARY KEY,
      source VARCHAR(50) DEFAULT NULL,
      name VARCHAR(150) DEFAULT NULL,
      email VARCHAR(150) DEFAULT NULL,
      phone VARCHAR(20) DEFAULT NULL,
      message TEXT DEFAULT NULL,
      metadata TEXT DEFAULT NULL,
      status VARCHAR(50) DEFAULT 'new',
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
  `,
  content_blocks: `
    CREATE TABLE IF NOT EXISTS content_blocks (
      id INT AUTO_INCREMENT PRIMARY KEY,
      page_key VARCHAR(100) NOT NULL,
      block_key VARCHAR(100) NOT NULL,
      title VARCHAR(255) DEFAULT NULL,
      body TEXT DEFAULT NULL,
      content_type VARCHAR(50) DEFAULT 'text',
      is_published TINYINT(1) DEFAULT 1,
      updated_by INT DEFAULT NULL,
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
      UNIQUE KEY uq_page_block (page_key, block_key)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
  `,
  media: `
    CREATE TABLE IF NOT EXISTS media (
      id INT AUTO_INCREMENT PRIMARY KEY,
      filename VARCHAR(255) NOT NULL,
      original_name VARCHAR(255) NOT NULL,
      mime_type VARCHAR(100) DEFAULT NULL,
      size INT DEFAULT NULL,
      category VARCHAR(50) DEFAULT 'other',
      alt_text VARCHAR(255) DEFAULT NULL,
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
  `,
  channels: `
    CREATE TABLE IF NOT EXISTS channels (
      id INT AUTO_INCREMENT PRIMARY KEY,
      name VARCHAR(150) NOT NULL,
      slug VARCHAR(150) UNIQUE NOT NULL,
      lcn VARCHAR(50) DEFAULT NULL,
      category VARCHAR(100) DEFAULT NULL,
      quality VARCHAR(50) DEFAULT NULL,
      access_type VARCHAR(50) DEFAULT NULL,
      logo_file VARCHAR(255) DEFAULT NULL,
      is_active TINYINT(1) DEFAULT 1,
      sort_order INT DEFAULT 0,
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
  `,
  dish_packages: `
    CREATE TABLE IF NOT EXISTS dish_packages (
      id INT AUTO_INCREMENT PRIMARY KEY,
      name VARCHAR(150) NOT NULL,
      slug VARCHAR(150) UNIQUE NOT NULL,
      package_type VARCHAR(50) DEFAULT NULL,
      price DECIMAL(10,2) DEFAULT 0.00,
      billing_cycle VARCHAR(50) DEFAULT 'monthly',
      description TEXT DEFAULT NULL,
      features TEXT DEFAULT NULL,
      pdf_file VARCHAR(255) DEFAULT NULL,
      include_fta TINYINT(1) DEFAULT 0,
      is_popular TINYINT(1) DEFAULT 0,
      is_active TINYINT(1) DEFAULT 1,
      sort_order INT DEFAULT 0,
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
  `,
  dish_package_channels: `
    CREATE TABLE IF NOT EXISTS dish_package_channels (
      package_id INT NOT NULL,
      channel_id INT NOT NULL,
      PRIMARY KEY (package_id, channel_id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
  `,
  dish_billing_terms: `
    CREATE TABLE IF NOT EXISTS dish_billing_terms (
      id INT AUTO_INCREMENT PRIMARY KEY,
      months INT NOT NULL,
      installation_price DECIMAL(10,2) DEFAULT 0.00,
      saving_amount DECIMAL(10,2) DEFAULT 0.00,
      sort_order INT DEFAULT 0,
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
  `,
  ott_apps: `
    CREATE TABLE IF NOT EXISTS ott_apps (
      id INT AUTO_INCREMENT PRIMARY KEY,
      name VARCHAR(150) NOT NULL,
      slug VARCHAR(150) UNIQUE NOT NULL,
      logo_file VARCHAR(255) DEFAULT NULL,
      is_active TINYINT(1) DEFAULT 1,
      sort_order INT DEFAULT 0,
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
  `,
  ott_packages: `
    CREATE TABLE IF NOT EXISTS ott_packages (
      id INT AUTO_INCREMENT PRIMARY KEY,
      name VARCHAR(150) NOT NULL,
      slug VARCHAR(150) UNIQUE NOT NULL,
      eyebrow VARCHAR(150) DEFAULT NULL,
      accent VARCHAR(50) DEFAULT NULL,
      tint VARCHAR(50) DEFAULT NULL,
      is_popular TINYINT(1) DEFAULT 0,
      is_active TINYINT(1) DEFAULT 1,
      sort_order INT DEFAULT 0,
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
  `,
  ott_package_apps: `
    CREATE TABLE IF NOT EXISTS ott_package_apps (
      package_id INT NOT NULL,
      app_id INT NOT NULL,
      PRIMARY KEY (package_id, app_id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
  `,
  ott_package_prices: `
    CREATE TABLE IF NOT EXISTS ott_package_prices (
      id INT AUTO_INCREMENT PRIMARY KEY,
      package_id INT NOT NULL,
      months INT NOT NULL,
      price DECIMAL(10,2) DEFAULT 0.00,
      playbox_pack_code VARCHAR(100) DEFAULT NULL,
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      UNIQUE KEY uq_package_months (package_id, months)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
  `,
  orders: `
    CREATE TABLE IF NOT EXISTS orders (
      id INT AUTO_INCREMENT PRIMARY KEY,
      name VARCHAR(150) DEFAULT NULL,
      email VARCHAR(150) DEFAULT NULL,
      phone VARCHAR(20) DEFAULT NULL,
      address TEXT DEFAULT NULL,
      city VARCHAR(100) DEFAULT NULL,
      message TEXT DEFAULT NULL,
      package_id INT DEFAULT NULL,
      package_type VARCHAR(50) DEFAULT NULL,
      months INT DEFAULT NULL,
      price DECIMAL(10,2) DEFAULT NULL,
      status VARCHAR(50) DEFAULT 'pending',
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
  `,
  audit_logs: `
    CREATE TABLE IF NOT EXISTS audit_logs (
      id INT AUTO_INCREMENT PRIMARY KEY,
      user_id INT DEFAULT NULL,
      action VARCHAR(255) NOT NULL,
      details TEXT DEFAULT NULL,
      ip_address VARCHAR(50) DEFAULT NULL,
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
  `
};

async function setup() {
  console.log("Connecting to MySQL Database...");
  let connection;
  try {
    // Connect without specifying database to create it if it doesn't exist
    connection = await mysql.createConnection({
      host: DB_HOST,
      user: DB_USER,
      password: DB_PASSWORD
    });

    console.log(`Creating database ${DB_NAME} if not exists...`);
    await connection.query(`CREATE DATABASE IF NOT EXISTS \`${DB_NAME}\`;`);
    await connection.changeUser({ database: DB_NAME });

    console.log("Creating tables...");
    for (const [tableName, query] of Object.entries(tables)) {
      console.log(`- Table: ${tableName}`);
      await connection.query(query);
    }

    // Check default admin user
    const [adminRows] = await connection.query("SELECT * FROM admin WHERE email = 'admin@wsshub.com'");
    if (adminRows.length === 0) {
      console.log("Inserting default admin user...");
      // Default password hash for 'admin'
      const defaultPasswordHash = "$2b$10$4xfuAnL9YPDBcpxQFBhWtO0ZK8jqNf8VjhBIKJiSHjg03w6eQhqtq";
      await connection.query(
        "INSERT INTO admin (name, email, password, role) VALUES (?, ?, ?, ?)",
        ["Administrator", "admin@wsshub.com", defaultPasswordHash, "admin"]
      );
      console.log("Default admin created successfully! (User: admin@wsshub.com, Password: admin)");
    } else {
      console.log("Admin user already exists.");
    }

    console.log("Database Setup Completed Successfully!");
  } catch (error) {
    console.error("Database Setup Failed:", error.message);
  } finally {
    if (connection) {
      await connection.end();
    }
  }
}

setup();
