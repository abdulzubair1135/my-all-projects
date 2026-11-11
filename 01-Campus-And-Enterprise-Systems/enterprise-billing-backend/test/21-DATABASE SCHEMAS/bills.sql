-- Table Schema for bills table (Header Table)
-- Main invoice/bill metadata for POS and Billing questions

CREATE TABLE IF NOT EXISTS bills (
    id INT AUTO_INCREMENT PRIMARY KEY,
    bill_number VARCHAR(50) NOT NULL UNIQUE,
    customer_id INT DEFAULT NULL,
    user_id INT NOT NULL, -- Cashier / Staff who generated the bill
    total_amount DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    discount_amount DECIMAL(10, 2) DEFAULT 0.00,
    tax_amount DECIMAL(10, 2) DEFAULT 0.00,
    grand_total DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    payment_mode ENUM('cash', 'card', 'upi') DEFAULT 'cash',
    status ENUM('paid', 'cancelled', 'refunded') DEFAULT 'paid',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE SET NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Sample Insert Data
INSERT INTO bills (bill_number, customer_id, user_id, total_amount, discount_amount, tax_amount, grand_total, payment_mode) VALUES
('INV-2026-0001', 1, 2, 998.00, 50.00, 170.64, 1118.64, 'upi');
