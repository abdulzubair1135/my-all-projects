# HTTP Status Codes One-Page Quick Revision Sheet

## Quick Exam Reference Table

| Code | Status | Meaning | When to Use in Controller |
| :--- | :--- | :--- | :--- |
| **200** | OK | Standard Success | Fetching data (`GET`), updating (`PUT`/`PATCH`), deleting (`DELETE`) |
| **201** | Created | Resource Created | Successfully creating record (`POST /api/products`, `POST /api/register`) |
| **400** | Bad Request | Validation Failed | Missing fields, invalid format from `express-validator` |
| **401** | Unauthorized | Auth Failed | Missing JWT, invalid password, expired token |
| **403** | Forbidden | Role Denied | Token valid but user lacks admin privileges (`role === 'customer'`) |
| **404** | Not Found | Route/Item Missing | ID does not exist in DB or invalid endpoint URL |
| **500** | Internal Error | Server Exception | DB connection failure, unhandled SQL query exception |

---

## Standard JSON Response Payload Examples

### Success Response
```json
{
  "success": true,
  "message": "Product created successfully",
  "data": { "id": 1, "name": "Mouse", "price": 499 }
}
```

### Error Response
```json
{
  "success": false,
  "message": "Resource not found",
  "error": "No product exists with ID 99"
}
```
