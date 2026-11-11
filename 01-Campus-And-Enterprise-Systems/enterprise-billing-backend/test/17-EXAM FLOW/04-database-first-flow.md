# Step 04: Database-First Flow & Setup

BCA practical me backend app connect karne se pehle MySQL database ready karna priority hoti hai.

---

## 1. Steps in MySQL Command Line / Workbench / phpMyAdmin
1. **Database Create karo:**
   ```sql
   CREATE DATABASE IF NOT EXISTS pos_db;
   USE pos_db;
   ```

2. **Tables execute karo (Foreign Key order me):**
   - Pehle Independent Tables create karo: `users`, `franchises`.
   - Baad me Dependent Tables create karo: `products` (depends on `franchises`), `bills` (depends on `users` & `franchises`).

3. **Sample Data Insert karo:**
   - Always insert 2-3 sample records so GET requests initial testing me output de sakein.

---

## 2. Node.js `config/db.js` Setup Checklist
- Standard `mysql2/promise` pool configuration:
```js
import mysql from 'mysql2/promise';
import dotenv from 'dotenv';

dotenv.config();

const pool = mysql.createPool({
  host: process.env.DB_HOST || 'localhost',
  user: process.env.DB_USER || 'root',
  password: process.env.DB_PASSWORD || '',
  database: process.env.DB_NAME || 'pos_db',
  waitForConnections: true,
  connectionLimit: 10,
  queueLimit: 0
});

export default pool;
```

- Key Check: Database configuration `.env` file se read honi chahiye.
