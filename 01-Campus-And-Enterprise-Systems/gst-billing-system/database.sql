CREATE DATABASE IF NOT EXISTS gst_billing_db;
USE gst_billing_db;

-- Users Table
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    state VARCHAR(50) NOT NULL,
    country VARCHAR(50) NOT NULL
);

-- Items Table
CREATE TABLE IF NOT EXISTS items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    item_name VARCHAR(100) NOT NULL,
    price DECIMAL(10, 2) NOT NULL
);

-- Bills Table
CREATE TABLE IF NOT EXISTS bills (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    item_id INT NOT NULL,
    customer_name VARCHAR(100) NOT NULL,
    customer_state VARCHAR(50) NOT NULL,
    customer_country VARCHAR(50) NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    gst_type VARCHAR(20) NOT NULL,
    gst_percentage DECIMAL(5, 2) NOT NULL,
    gst_amount DECIMAL(10, 2) NOT NULL,
    final_amount DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (item_id) REFERENCES items(id) ON DELETE CASCADE
);

-- Insert Sample Data
INSERT INTO users (name, email, password, state, country) VALUES 
('Rajesh Seller', 'rajesh@example.com', 'password123', 'Gujarat', 'India');

INSERT INTO items (item_name, price) VALUES 
('Laptop', 50000.00),
('Smartphone', 25000.00),
('Office Chair', 7500.00);
