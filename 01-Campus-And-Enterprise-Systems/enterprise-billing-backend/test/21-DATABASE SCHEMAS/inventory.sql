-- Table Schema for inventory table
-- Links Products to Franchises/Warehouses with stock management

CREATE TABLE IF NOT EXISTS inventory (
    id INT AUTO_INCREMENT PRIMARY KEY,
    franchise_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL DEFAULT 0,
    min_threshold INT NOT NULL DEFAULT 5,
    last_restocked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (franchise_id) REFERENCES franchises(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
    UNIQUE KEY unique_franchise_product (franchise_id, product_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Sample Insert Data
INSERT INTO inventory (franchise_id, product_id, quantity, min_threshold) VALUES
(1, 1, 40, 10),
(1, 2, 15, 5),
(2, 1, 30, 5);
