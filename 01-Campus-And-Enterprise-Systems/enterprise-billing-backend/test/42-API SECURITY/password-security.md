# Password Hashing and Security with `bcrypt` (`password-security.md`)

Never store passwords in plain text in a database! Plaintext storage exposes user credentials if database records are compromised. Always hash passwords using `bcrypt` before storing them.

---

## 1. How `bcrypt` Works

- **Salting**: `bcrypt` automatically generates a random salt (random bytes) appended to passwords before hashing to defeat rainbow table dictionary attacks.
- **Salt Rounds**: The cost factor determining computational difficulty. Recommended standard salt rounds: `10`.

---

## 2. Hashing Passwords During User Registration

```javascript
import bcrypt from 'bcrypt';

export const hashPassword = async (plainPassword) => {
  const saltRounds = 10;
  const hashedPassword = await bcrypt.hash(plainPassword, saltRounds);
  return hashedPassword;
};
```

---

## 3. Comparing Passwords During User Login

```javascript
export const comparePassword = async (plainPassword, hashedPasswordFromDB) => {
  // Returns boolean true if match, false if invalid
  const isMatch = await bcrypt.compare(plainPassword, hashedPasswordFromDB);
  return isMatch;
};
```

---

## 4. Complete Registration & Authentication Example

```javascript
// Registration Handler
export const registerUser = async (req, res, next) => {
  try {
    const { name, email, password } = req.body;
    
    // Hash plain password
    const hashedPassword = await bcrypt.hash(password, 10);

    // Save hashedPassword into MySQL
    const [result] = await pool.query(
      'INSERT INTO users (name, email, password) VALUES (?, ?, ?)',
      [name, email, hashedPassword]
    );

    res.status(201).json({ success: true, message: 'User registered' });
  } catch (err) {
    next(err);
  }
};

// Login Handler
export const loginUser = async (req, res, next) => {
  try {
    const { email, password } = req.body;

    const [rows] = await pool.query('SELECT * FROM users WHERE email = ?', [email]);
    if (rows.length === 0) {
      return res.status(401).json({ success: false, message: 'Invalid credentials' });
    }

    const user = rows[0];
    const isPasswordValid = await bcrypt.compare(password, user.password);

    if (!isPasswordValid) {
      return res.status(401).json({ success: false, message: 'Invalid credentials' });
    }

    // Generate JWT Token...
    res.status(200).json({ success: true, message: 'Login successful' });
  } catch (err) {
    next(err);
  }
};
```
