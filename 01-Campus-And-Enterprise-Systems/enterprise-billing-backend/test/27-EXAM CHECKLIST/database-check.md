# Database Verification Checklist

## Database Integrity Checklist

- [ ] **Database Connection Pool**: `pool.query()` succeeds without connection timeout.
- [ ] **Table Constraints**: Primary Keys (`AUTO_INCREMENT`) and Foreign Keys (`ON DELETE CASCADE` / `SET NULL`) correctly set up.
- [ ] **Unique Constraints**: Email, product barcode, franchise codes marked as `UNIQUE`.
- [ ] **Data Types**: Prices use `DECIMAL(10,2)`, quantities use `INT`, passwords use `VARCHAR(255)`.
- [ ] **MySQL Transactions**: Multi-table inserts (`bills` & `bill_items`) use `beginTransaction()`, `commit()`, `rollback()`, and `release()`.
- [ ] **Stock Updates**: Placing an order/bill automatically decrements `stock` in `products` table.
