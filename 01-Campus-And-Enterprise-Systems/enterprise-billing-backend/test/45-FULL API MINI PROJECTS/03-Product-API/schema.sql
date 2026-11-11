CREATE DATABASE IF NOT EXISTS product_db;
USE product_db;

CREATE TABLE IF NOT EXISTS products (
  id INT AUTO_INCREMENT PRIMARY KEY,
  sku VARCHAR(30) NOT NULL UNIQUE,
  title VARCHAR(150) NOT NULL,
  description TEXT,
  price DECIMAL(10,2) NOT NULL,
  stock INT NOT NULL DEFAULT 0,
  category VARCHAR(50) NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO products (sku, title, description, price, stock, category) VALUES
('LAP-101', 'Dell XPS 13', 'High performance ultra laptop', 120000.00, 15, 'Electronics'),
('PHN-202', 'iPhone 15', 'Apple smartphone with A16 Bionic', 79900.00, 30, 'Electronics'),
('BOK-303', 'Node.js Mastery', 'Complete backend guide', 599.00, 100, 'Books');
