# 400 Bad Request Error Guide (`400-errors.md`)

The `400 Bad Request` HTTP status code indicates that the server cannot process the request due to something perceived as a client error (e.g. malformed request syntax, invalid query parameters, missing required payload properties, or failed validation).

---

## 1. When to Return HTTP 400

- Validation failure (e.g., `express-validator` rules failed).
- Missing required fields in `req.body` (e.g. missing `email` or `password`).
- Invalid parameter data types (e.g., passing `"abc"` where integer `:id` is expected).
- Malformed JSON payload in the request body.

---

## 2. Standard 400 Response Format

```json
{
  "success": false,
  "message": "Validation failed for request parameters",
  "error": [
    {
      "field": "age",
      "message": "Age must be a positive integer"
    }
  ]
}
```

---

## 3. Express Controller Example

```javascript
export const updateAge = (req, res) => {
  const { age } = req.body;
  if (!age || typeof age !== 'number' || age < 1) {
    return res.status(400).json({
      success: false,
      message: 'Invalid request',
      error: 'Field "age" must be a positive number'
    });
  }
  
  res.status(200).json({ success: true, message: 'Age updated successfully' });
};
```
