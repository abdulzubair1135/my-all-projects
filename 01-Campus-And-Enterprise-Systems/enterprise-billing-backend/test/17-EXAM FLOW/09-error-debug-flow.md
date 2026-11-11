# Step 09: Error Debugging & Troubleshooting Checklist

Exam time me error aaye to panic nahi hona! Follow this systematic debugging guide:

---

## 1. Common Errors & Quick Solutions

### A. `ECONNREFUSED` / Database Connection Error
- **Cause:** MySQL service running nahi hai ya host/port mismatch hai.
- **Fix:** XAMPP/MySQL service restart karo. `.env` me `DB_HOST`, `DB_USER`, `DB_PASSWORD`, `DB_NAME` check karo.

### B. `Cannot POST /api/...` or `404 Not Found`
- **Cause:** Route URL missing, wrong HTTP verb, or route `app.use()` me registered nahi hai.
- **Fix:** `server.js` me check karo path prefix match hota hai ya nahi.

### C. `jwt must be provided` or `jwt malformed` / `401 Unauthorized`
- **Cause:** Authorization header missing, or format `"Bearer <token>"` strictly follow nahi kiya.
- **Fix:** Postman me `Authorization: Bearer <token>` set karo without quotes.

### D. Syntax Error `Cannot use import statement outside a module`
- **Cause:** `"type": "module"` in `package.json` missing hai.
- **Fix:** Add `"type": "module"` in `package.json`.

---

## 2. Debugging Commands Sequence
```bash
# Check node process & syntax
node server.js

# Check environment variables
console.log(process.env.DB_NAME);

# Print SQL Queries if error occurs
console.error("SQL Error:", error.message);
```
