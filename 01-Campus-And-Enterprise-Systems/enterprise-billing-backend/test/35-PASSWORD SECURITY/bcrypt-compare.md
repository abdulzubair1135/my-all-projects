# Bcrypt Password Comparison Guide (`bcrypt.compare`)

## 1. How Does Password Verification Work?
Since bcrypt hashing is a one-way operation, you CANNOT decrypt the saved database hash to check if it equals the user's login input password.

Instead, `bcrypt.compare(plainTextInput, hashedPasswordFromDB)` takes the incoming raw password string, extracts the embedded salt from the hashed string, re-hashes the input with that salt, and compares the resulting hashes in constant time to prevent timing attacks.

---

## 2. Node.js Code Example (ES Modules)

```js
import bcrypt from 'bcrypt';

export const verifyPassword = async (inputPassword, storedHash) => {
  // Returns boolean true or false
  const isMatch = await bcrypt.compare(inputPassword, storedHash);
  return isMatch;
};

// Usage:
// const isValid = await verifyPassword('SecretPass123', '$2b$10$EixZaYVK1fsbw1Zfb...');
// if (isValid) { loginSuccess(); } else { return 401; }
```

---

## 3. Exam Notes & Rules
- Never use `==` or `===` operator to compare plain text passwords with database hashes!
- Always use `await bcrypt.compare(plainPassword, hashedPassword)`.
