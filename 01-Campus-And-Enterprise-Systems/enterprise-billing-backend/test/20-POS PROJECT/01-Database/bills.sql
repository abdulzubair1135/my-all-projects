-- Sample Bills Insert Queries
USE pos_db;

INSERT INTO bills (bill_number, franchise_id, user_id, customer_name, subtotal, tax_rate, tax_amount, grand_total, items_json) VALUES
('INV-20260817-001', 1, 2, 'Vikram Singh', 370.00, 0.18, 66.60, 436.60, '[{"product_id": 1, "name": "Espresso Coffee", "price": 150, "quantity": 1}, {"product_id": 2, "name": "Chicken Burger", "price": 220, "quantity": 1}]');
