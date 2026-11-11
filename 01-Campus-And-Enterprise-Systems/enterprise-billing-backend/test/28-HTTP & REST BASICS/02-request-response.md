# HTTP Request and Response Architecture

## 1. HTTP Request Structure
An HTTP Request consists of 3 main parts sent from client to server:

```
[Request Line]     -> METHOD /path HTTP/1.1
[Headers]          -> Host, Content-Type, Authorization, etc.
[Body] (Optional)  -> JSON / Form Data (for POST, PUT, PATCH)
```

### Raw Request Example:
```http
POST /api/students HTTP/1.1
Host: localhost:5000
Content-Type: application/json
Authorization: Bearer eyJhbGciOiJIUzI1Ni...

{
  "name": "Amit Kumar",
  "course": "BCA",
  "semester": 4
}
```

---

## 2. HTTP Response Structure
An HTTP Response consists of 3 main components sent from server back to client:

```
[Status Line]     -> HTTP/1.1 200 OK
[Headers]         -> Content-Type, Set-Cookie, Access-Control-Allow-Origin
[Body]            -> Data payload (JSON, HTML, plain text)
```

### Raw Response Example:
```http
HTTP/1.1 201 Created
Content-Type: application/json; charset=utf-8
Date: Mon, 17 Aug 2026 12:00:00 GMT

{
  "success": true,
  "message": "Student created successfully",
  "data": {
    "id": 42,
    "name": "Amit Kumar",
    "course": "BCA",
    "semester": 4
  }
}
```

---

## 3. Data Flow in Express.js Backend

```
Client (Browser / Postman / Mobile App)
        |
        v  (HTTP Request: URL, Headers, Body)
Express Server (app.js / server.js)
        |
        v  (Middleware / Routing / Controller)
Database Query (MySQL query via mysql2/promise)
        |
        v  (Database Result Array / Row)
Express Response formatting (res.status(200).json({...}))
        |
        v  (HTTP Response: Status Code, Headers, JSON Body)
Client receives response
```

---

## 4. Exam Summary & Notes
- **Request Line components**: Method, Request URI, HTTP Version.
- **Response Line components**: HTTP Version, Status Code, Reason Phrase.
- **Express Request Object (`req`)**: Encapsulates all incoming headers, params, query, body.
- **Express Response Object (`res`)**: Provides helper methods like `res.status()`, `res.json()`, `res.send()`.
