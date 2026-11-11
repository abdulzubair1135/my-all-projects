# 409 Conflict Error Guide (`409-errors.md`)

The `409 Conflict` HTTP status code indicates that the request could not be processed because of a conflict in the current state of the resource, such as attempting to create a record with a unique value (email, username, phone number) that already exists in the database.

---

## 1. When to Return HTTP 409

- Registering a user with an email address already registered.
- Assigning a roll number or username that violates a MySQL `UNIQUE` constraint.
- Race conditions or conflicting resource updates.

---

## 2. Standard 409 Response Format

```json
{
  "success": false,
  "message": "User registration failed. Email address is already registered.",
  "error": "DUPLICATE_ENTRY"
}
```

---

## 3. MySQL Duplicate Entry Handling Example

```javascript
export const registerUser = async (req, res, next) => {
  const { username, email, password } = req.body;
  try {
    // 1. Check before insertion
    const [existing] = await pool.query('SELECT id FROM users WHERE email = ?', [email]);
    if (existing.length > 0) {
      return res.status(409).json({
        success: false,
        message: 'Account with this email already exists',
        error: 'EMAIL_ALREADY_EXISTS'
      });
    }

    // 2. Insert new user
    const [result] = await pool.query(
      'INSERT INTO users (username, email, password) VALUES (?, ?, ?)',
      [username, email, password]
    );

    res.status(201).json({
      success: true,
      message: 'User registered successfully',
      data: { id: result.insertId, username, email }
    });
  } catch (error) {
    if (error.code === 'ER_DUP_ENTRY') {
      return res.status(409).json({
        success: false,
        message: 'Duplicate entry detected in database',
        error: error.sqlMessage
      });
    }
    next(error);
  }
};
```
