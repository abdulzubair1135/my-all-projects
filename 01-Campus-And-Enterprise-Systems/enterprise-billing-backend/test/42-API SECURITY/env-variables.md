# Environment Variable Management with `dotenv` (`env-variables.md`)

Environment variables keep sensitive configuration settings (database passwords, API keys, JWT secrets) out of source control code repositories like Git.

---

## 1. Setting Up `dotenv`

```bash
npm install dotenv
```

Load `dotenv` at the top of your entry file (`server.js` or `index.js`):

```javascript
import dotenv from 'dotenv';
dotenv.config();

// Access variables via process.env
const PORT = process.env.PORT || 5000;
const DB_HOST = process.env.DB_HOST || 'localhost';
```

---

## 2. Sample `.env` Configuration File

Create `.env` in your root directory:

```env
PORT=5000
NODE_ENV=development

# MySQL Database Configuration
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=secretpassword
DB_NAME=college_db

# Security & JWT Configuration
JWT_SECRET=super_secret_jwt_key_bca_2026
JWT_EXPIRES_IN=1d
```

---

## 3. Sample `.env.example` File

> [!IMPORTANT]
> Never commit your real `.env` file to Git! Add `.env` to `.gitignore` and commit a `.env.example` file instead with placeholder values.

```env
PORT=5000
NODE_ENV=development

DB_HOST=localhost
DB_PORT=3306
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_NAME=your_db_name

JWT_SECRET=your_jwt_secret_key
JWT_EXPIRES_IN=1d
```
