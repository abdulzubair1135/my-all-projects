# Bcrypt Password Hashing One-Page Quick Revision Sheet

## What is Bcrypt?
Bcrypt is a password-hashing function based on the Blowfish cipher. It incorporates a salt to protect against rainbow table attacks.

---

## 1. Password Hashing (User Registration)
```javascript
import bcrypt from 'bcrypt';

const plainPassword = 'UserPassword123';
const saltRounds = 10;

// Hash password
const hashedPassword = await bcrypt.hash(plainPassword, saltRounds);
// Save hashedPassword to MySQL database
```

---

## 2. Password Comparison (User Login)
```javascript
import bcrypt from 'bcrypt';

// Compare entered plain text password with stored DB hash
const isMatch = await bcrypt.compare(enteredPassword, userFromDb.password);

if (!isMatch) {
    return res.status(401).json({ success: false, message: 'Invalid credentials' });
}
```

---

## Key Exam Rule
Never store unhashed plain text passwords in the database! Always use `await bcrypt.hash(password, 10)` before running `INSERT INTO users`.
