# Handling & Formatting Validation Errors (`validation-errors.md`)

When validation fails in a REST API, returning clear, formatted error messages helps frontend developers and clients identify exact issues easily.

---

## 1. Raw Output vs Formatted Output

### Raw Output from `validationResult(req).array()`
Default `express-validator` output contains verbose metadata:
```json
[
  {
    "type": "field",
    "value": "invalid-email",
    "msg": "Please provide a valid email address",
    "path": "email",
    "location": "body"
  }
]
```

### Clean Formatted Output (Recommended Standard)
```json
{
  "success": false,
  "message": "Validation failed",
  "errors": [
    {
      "field": "email",
      "message": "Please provide a valid email address"
    }
  ]
}
```

---

## 2. Formatting Helper Function

```javascript
import { validationResult } from 'express-validator';

export const handleValidationErrors = (req, res, next) => {
  const errors = validationResult(req);
  
  if (!errors.isEmpty()) {
    // Map errors to clean field-message pairs
    const errorList = errors.array().map(error => ({
      field: error.path,
      message: error.msg
    }));

    return res.status(400).json({
      success: false,
      message: 'Validation failed',
      errors: errorList
    });
  }

  next();
};
```

---

## 3. Formatting Errors as a Key-Value Map

Sometimes client applications prefer a mapped object format instead of an array:

```javascript
// Output format: { email: "Invalid email", password: "Too short" }
const mappedErrors = errors.array().reduce((acc, curr) => {
  acc[curr.path] = curr.msg;
  return acc;
}, {});

return res.status(400).json({
  success: false,
  message: 'Validation failed',
  errors: mappedErrors
});
```

---

## 4. Key Takeaways for BCA Practical Exams

1. **Status Code**: Always return `400 Bad Request`.
2. **Success Flag**: Include `"success": false`.
3. **Array or Object**: Standardize error format across all endpoints.
4. **Never Leak Stack Traces**: Validation errors are operational client input errors, so stack traces should not be included.
