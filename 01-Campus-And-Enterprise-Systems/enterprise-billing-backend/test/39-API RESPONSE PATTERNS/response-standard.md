# REST API Response Standard Specification (`response-standard.md`)

Consistent API response formatting makes client integration predictable and simplifies frontend error handling. This document details the standard JSON response format used across all REST API endpoints.

---

## 1. Response Structure Rules

Every HTTP response returned by the API MUST contain:
1. `success` (`boolean`): Indicates whether the request succeeded (`true`) or failed (`false`).
2. `message` (`string`): A user-friendly message describing the outcome.
3. `data` (`object` / `array` / `null`): Present on success responses.
4. `error` (`string` / `array` / `null`): Present on error responses.

---

## 2. HTTP Status Code Mapping

| HTTP Code | Name | Scenario |
| :--- | :--- | :--- |
| **200 OK** | Success | Standard successful GET, PUT, PATCH request |
| **201 Created** | Created | Successful POST creation request |
| **400 Bad Request** | Validation Failure | Invalid input, missing required parameters |
| **401 Unauthorized** | Unauthenticated | Missing or expired JWT token, invalid credentials |
| **403 Forbidden** | Unauthorized Role | Insufficient permissions (e.g. Student trying Admin route) |
| **404 Not Found** | Not Found | Target ID or route endpoint does not exist |
| **409 Conflict** | Resource Conflict | Duplicate email or unique constraint violation |
| **500 Internal Error** | Server Error | Unhandled database error or system crash |

---

## 3. Example JSON Contracts

### A. General Success (200 OK)
```json
{
  "success": true,
  "message": "Student record updated successfully",
  "data": {
    "id": 101,
    "name": "Amit Kumar",
    "course": "BCA"
  }
}
```

### B. Resource Created (201 Created)
```json
{
  "success": true,
  "message": "New course added successfully",
  "data": {
    "id": 5,
    "course_code": "BCA301",
    "title": "Database Management Systems"
  }
}
```

### C. Paginated Response (200 OK)
```json
{
  "success": true,
  "message": "Students retrieved successfully",
  "data": [
    { "id": 1, "name": "Aarav" },
    { "id": 2, "name": "Bhavna" }
  ],
  "pagination": {
    "currentPage": 1,
    "limit": 10,
    "totalRecords": 45,
    "totalPages": 5,
    "hasNextPage": true,
    "hasPrevPage": false
  }
}
```

### D. Validation Error (400 Bad Request)
```json
{
  "success": false,
  "message": "Validation failed",
  "error": [
    { "field": "email", "message": "Email is invalid" },
    { "field": "age", "message": "Age must be >= 18" }
  ]
}
```

### E. Authentication / Server Error (401 / 500)
```json
{
  "success": false,
  "message": "Token has expired. Please login again.",
  "error": "TOKEN_EXPIRED"
}
```
