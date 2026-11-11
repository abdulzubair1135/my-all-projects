# Bcrypt Hashing Explanation & Guide

## 1. Why Plain Text Passwords Must Never Be Stored
Storing plain-text passwords in databases is a severe security vulnerability. If a data breach occurs, attacker gets full access to user credentials.

---

## 2. Hashing vs Encryption
- **Encryption**: Two-way operation (Data can be decrypted back to plain text using a secret key).
- **Hashing**: One-way algorithm (Data is converted into a fixed-length string and CANNOT be converted back to plain text).

---

## 3. What is Salt & Salt Rounds in Bcrypt?
- **Salt**: Random secret string added to password before hashing to prevent Rainbow Table attacks (dictionary lookup of precomputed hashes).
- **Salt Rounds (Cost Factor)**: Controls how much time is needed to calculate a single bcrypt hash.
  - Recommended salt rounds for web applications: **10** (balances computational security and server response speed).

---

## 4. Node.js Code Example (ES Modules)

```js
import bcrypt from 'bcrypt';

const hashPassword = async (plainPassword) => {
  const saltRounds = 10;
  // Generates salt and hashes password in one step
  const hashedPassword = await bcrypt.hash(plainPassword, saltRounds);
  return hashedPassword;
};

// Example output: $2b$10$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW
```
