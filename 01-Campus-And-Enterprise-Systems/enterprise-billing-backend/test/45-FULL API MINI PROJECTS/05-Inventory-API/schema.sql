CREATE DATABASE IF NOT EXISTS inventory_db;
USE inventory_db;

CREATE TABLE IF NOT EXISTS inventory_items (
  id INT AUTO_INCREMENT PRIMARY KEY,
  item_code VARCHAR(30) NOT NULL UNIQUE,
  item_name VARCHAR(100) NOT NULL,
  quantity INT NOT NULL DEFAULT 0,
  min_level INT NOT NULL DEFAULT 5,
  supplier VARCHAR(100) NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO inventory_items (item_code, item_name, quantity, min_level, supplier) VALUES
('INV-001', 'USB Type-C Cable', 150, 20, 'TechSupplies Ltd'),
('INV-002', 'Wireless Mouse', 45, 10, 'LogiCorp Inc'),
('INV-003', 'Mechanical Keyboard', 8, 10, 'KeyCraft Tech');
