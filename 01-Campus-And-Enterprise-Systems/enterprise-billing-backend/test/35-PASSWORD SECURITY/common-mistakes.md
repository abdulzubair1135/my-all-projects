# Common Password Security Mistakes in Exams & Practical Tests

## 1. Top Mistakes Students Make in BCA Exams

| Mistake | Why it fails | Correct Approach |
|---------|--------------|------------------|
| **Storing raw passwords** | Severe vulnerability. DB leak exposes passwords. | Hash with `bcrypt.hash(pwd, 10)` before SQL query. |
| **Using MD5 / SHA1** | MD5 and SHA1 are obsolete and fast to crack. | Use `bcrypt` or `argon2`. |
| **Comparing strings directly (`pwd === dbHash`)** | Hash is unique each time due to random salt; string match fails. | Use `await bcrypt.compare(inputPwd, dbHash)`. |
| **Returning password in JSON response** | Exposes hash to frontend/client unnecessarily. | Exclude password field: `const { password, ...userData } = user;` |
| **Specific Error Messages on Login** | Revealing "Email not found" allows attackers to harvest valid emails. | Use generic messages like "Invalid email or password". |
| **Low Salt Rounds (e.g. 1 or 2)** | Insecure, easier to brute force. | Use `saltRounds = 10`. |

---

## 2. Quick Exam Viva Question
- **Q**: Why does `bcrypt.hash("123456", 10)` generate a completely different hash string every single execution?
- **A**: Because `bcrypt` automatically generates a random cryptographic **salt** for every hashing operation. The salt is embedded inside the resulting hash string, so no two hashes of the same password look alike.
