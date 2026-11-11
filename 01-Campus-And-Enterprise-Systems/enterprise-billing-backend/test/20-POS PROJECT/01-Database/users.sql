-- Sample Users Insert Queries
USE pos_db;

-- Password for both users is 'password123' (bcrypt hashed)
INSERT INTO users (name, email, password, role) VALUES
('Admin Manager', 'admin@pos.com', '$2b$10$wN1rBshY2uP5H9d8hUqR0.aR5hL8O2gH0V3O4j5k6l7m8n9o0p1q2', 'admin'),
('Rahul Cashier', 'rahul@pos.com', '$2b$10$wN1rBshY2uP5H9d8hUqR0.aR5hL8O2gH0V3O4j5k6l7m8n9o0p1q2', 'cashier');
