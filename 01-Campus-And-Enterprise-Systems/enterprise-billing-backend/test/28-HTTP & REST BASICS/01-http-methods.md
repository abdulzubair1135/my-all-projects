# HTTP Methods (Verbs) Guide for Backend Development & Exams

## Overview
HTTP (Hypertext Transfer Protocol) methods indicate the desired action to be performed on a given resource. In RESTful API design, HTTP verbs correspond directly to CRUD operations (Create, Read, Update, Delete).

---

## Standard HTTP Methods

| HTTP Method | CRUD Operation | Description | Request Body | Safe? | Idempotent? |
|-------------|----------------|-------------|--------------|-------|-------------|
| **GET** | Read | Retrieve data from server | No | Yes | Yes |
| **POST** | Create | Create a new resource | Yes | No | No |
| **PUT** | Update (Replace) | Replace entire resource | Yes | No | Yes |
| **PATCH** | Update (Partial) | Modify partial fields | Yes | No | No |
| **DELETE** | Delete | Remove a resource | Optional (Usually No) | No | Yes |

---

## Detailed Explanation & Use Cases

### 1. GET (Read)
- **Purpose**: Used to fetch data from the server.
- **Key Characteristics**: Should never modify server data (Safe and Idempotent).
- **Example Route**: `GET /api/users` or `GET /api/users/5`
- **Express Example**:
```js
app.get('/api/users/:id', async (req, res) => {
  const { id } = req.params;
  // Fetch user logic
  res.status(200).json({ success: true, data: { id, name: "Rahul Sharma" } });
});
```

### 2. POST (Create)
- **Purpose**: Submits data to be processed by a specified resource, usually resulting in a creation of a new record.
- **Key Characteristics**: Not safe, not idempotent (multiple identical POST calls create multiple records).
- **Example Route**: `POST /api/users`
- **Express Example**:
```js
app.post('/api/users', async (req, res) => {
  const { name, email } = req.body;
  // Insert user logic
  res.status(201).json({ success: true, message: "User created successfully", data: { id: 101, name, email } });
});
```

### 3. PUT (Full Update / Replace)
- **Purpose**: Replaces all current representations of the target resource with the request payload.
- **Key Characteristics**: Idempotent (calling it multiple times with identical payload yields identical server state).
- **Example Route**: `PUT /api/users/5`
- **Payload Requirement**: Complete user object (if a field is omitted, it gets overwritten/reset).

### 4. PATCH (Partial Update)
- **Purpose**: Applies partial modifications to a resource.
- **Key Characteristics**: Only updates specified fields without altering unmentioned fields.
- **Example Route**: `PATCH /api/users/5`
- **Payload Example**: `{ "email": "newemail@example.com" }`

### 5. DELETE (Remove)
- **Purpose**: Deletes the specified resource.
- **Key Characteristics**: Idempotent (subsequent DELETEs for an already deleted ID yield the same final state or 404).
- **Example Route**: `DELETE /api/users/5`

---

## Key Terms for Exam Definition

1. **Safe Method**: An HTTP method that does not modify the state of the server (e.g., `GET`, `HEAD`).
2. **Idempotent Method**: An HTTP method where multiple identical requests produce the exact same server state as a single request (e.g., `GET`, `PUT`, `DELETE`).

---

## Exam Tip Questions
- **Q**: What is the difference between `PUT` and `PATCH`?
  - **A**: `PUT` replaces the *entire* resource representation, requiring all fields in the request. `PATCH` applies *partial* updates, updating only the fields provided.
- **Q**: Why is `POST` neither safe nor idempotent?
  - **A**: Because sending multiple identical `POST` requests creates multiple duplicate entities on the database.
