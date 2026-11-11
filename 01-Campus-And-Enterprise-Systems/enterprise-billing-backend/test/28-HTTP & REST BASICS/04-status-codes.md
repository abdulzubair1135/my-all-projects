# HTTP Status Codes Guide for Backend Exams & Development

## 1. Status Code Categories Overview

HTTP status codes are 3-digit integers returned by the server indicating the result of a request.

| Range | Category | Purpose |
|-------|----------|---------|
| **1xx** | Informational | Request received, continuing process |
| **2xx** | Success | Request was successfully received, understood, and accepted |
| **3xx** | Redirection | Further action needs to be taken to complete request |
| **4xx** | Client Error | Request contains bad syntax or cannot be fulfilled |
| **5xx** | Server Error | Server failed to fulfill an apparently valid request |

---

## 2. Top HTTP Status Codes to Remember for Exams

### 2xx Success
- **`200 OK`**: Standard success response (GET, PUT, DELETE, PATCH).
- **`201 Created`**: Resource created successfully (POST).
- **`204 No Content`**: Action succeeded, but no body is returned (DELETE).

### 4xx Client Errors
- **`400 Bad Request`**: Missing/invalid fields in payload or validation error.
- **`401 Unauthorized`**: Authentication missing or token invalid/expired.
- **`403 Forbidden`**: Authenticated user lacks permission/roles for resource.
- **`404 Not Found`**: Resource or route endpoint does not exist.
- **`409 Conflict`**: Database unique constraint failure (e.g., email already registered).
- **`422 Unprocessable Entity`**: Semantic validation failure.

### 5xx Server Errors
- **`500 Internal Server Error`**: Unhandled exception, database crash, syntax error.
- **`502 Bad Gateway`**: Upstream server issue.
- **`503 Service Unavailable`**: Server is temporary down or overloaded.

---

## 3. Express Code Standard Usage Example

```js
import express from 'express';
const app = express();
app.use(express.json());

// 200 OK
app.get('/api/users', (req, res) => {
  res.status(200).json({ success: true, message: "Users fetched", data: [] });
});

// 201 Created
app.post('/api/users', (req, res) => {
  res.status(201).json({ success: true, message: "User registered", data: { id: 1 } });
});

// 400 Bad Request
app.post('/api/login', (req, res) => {
  if (!req.body.email) {
    return res.status(400).json({ success: false, message: "Email is required", error: "BAD_REQUEST" });
  }
});

// 401 Unauthorized
app.get('/api/profile', (req, res) => {
  return res.status(401).json({ success: false, message: "Access denied. Token missing.", error: "UNAUTHORIZED" });
});

// 404 Not Found
app.use((req, res) => {
  res.status(404).json({ success: false, message: "Route not found", error: "NOT_FOUND" });
});
```

---

## 4. Quick Exam Cheat Sheet Table

| Scenario | Status Code | Reason |
|----------|-------------|--------|
| Successful GET request | `200` | OK |
| Successful POST creation | `201` | Created |
| Validation error (missing name) | `400` | Bad Request |
| Wrong Password or No Token | `401` | Unauthorized |
| User tries to access Admin route | `403` | Forbidden |
| User ID not found in MySQL | `404` | Not Found |
| Email already exists | `409` | Conflict |
| Database Connection Failed | `500` | Internal Server Error |
