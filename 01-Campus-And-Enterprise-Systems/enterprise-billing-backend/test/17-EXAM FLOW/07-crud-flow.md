# Step 07: Standard CRUD Flow

CRUD stands for Create, Read, Update, Delete. Exam me resource management standard step sequence:

---

## 1. Create (POST `/api/resource`)
- Client sends JSON payload in request body.
- Route validation rule checks required fields.
- Controller calls Model method: `INSERT INTO table (fields) VALUES (?, ?)`.
- Returns `201 Created` with newly created item or inserted ID.

## 2. Read All (GET `/api/resource`)
- Controller calls Model method: `SELECT * FROM table`.
- Returns array of data inside `"data": [...]`.

## 3. Read Single (GET `/api/resource/:id`)
- Extracts `id` from `req.params.id`.
- Model executes: `SELECT * FROM table WHERE id = ?`.
- Check if record exists; if not return `404 Not Found`.
- Returns object inside `"data": { ... }`.

## 4. Update (PUT `/api/resource/:id`)
- Extracts `id` and new payload fields.
- Verify record exists before updating.
- Model executes: `UPDATE table SET field1=?, field2=? WHERE id=?`.
- Returns updated item or success message.

## 5. Delete (DELETE `/api/resource/:id`)
- Extracts `id` from `req.params.id`.
- Verify record exists.
- Model executes: `DELETE FROM table WHERE id=?`.
- Returns success deletion response.
