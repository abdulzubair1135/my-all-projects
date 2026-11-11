# SET 01 - Express & MySQL Basic CRUD Operations

## Question
Create an Express.js REST API for a **Library Book Management System** using MySQL (`mysql2/promise`) and ES Modules.

---

## Requirements
1. Use ES Modules (`import`/`export`) with `"type": "module"` in `package.json`.
2. Connect to a MySQL database named `library_db`.
3. Table `books`: `id`, `isbn` (UNIQUE), `title`, `author`, `publication_year`, `genre`.
4. Implement full CRUD routes:
   - `GET /api/books` - Get all books.
   - `GET /api/books/:id` - Get a single book by ID.
   - `POST /api/books` - Add a new book.
   - `PUT /api/books/:id` - Update existing book.
   - `DELETE /api/books/:id` - Remove a book.
5. Standard Response Format:
   - Success: `{ "success": true, "message": "...", "data": ... }`
   - Error: `{ "success": false, "message": "...", "error": "..." }`

---

## Hints
- Use `pool.query(sql, [params])` to avoid SQL Injection.
- Return HTTP 404 when a book with the given ID is not found (`affectedRows === 0`).
- Handle duplicate `isbn` errors gracefully.

---

## Expected Structure
```text
SET-01-CRUD/
├── config/
│   └── db.js
├── models/
│   └── bookModel.js
├── controllers/
│   └── bookController.js
├── routes/
│   └── bookRoutes.js
├── server.js
├── schema.sql
└── package.json
```

---

## Solution Code

### 1. `schema.sql`
```sql
CREATE DATABASE IF NOT EXISTS library_db;
USE library_db;

CREATE TABLE IF NOT EXISTS books (
  id INT AUTO_INCREMENT PRIMARY KEY,
  isbn VARCHAR(20) NOT NULL UNIQUE,
  title VARCHAR(150) NOT NULL,
  author VARCHAR(100) NOT NULL,
  publication_year INT NOT NULL,
  genre VARCHAR(50) NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 2. `config/db.js`
```javascript
import mysql from 'mysql2/promise';

const pool = mysql.createPool({
  host: 'localhost',
  user: 'root',
  password: '',
  database: 'library_db',
  waitForConnections: true,
  connectionLimit: 10
});

export default pool;
```

### 3. `models/bookModel.js`
```javascript
import pool from '../config/db.js';

export const findAll = async () => {
  const [rows] = await pool.query('SELECT * FROM books ORDER BY id DESC');
  return rows;
};

export const findById = async (id) => {
  const [rows] = await pool.query('SELECT * FROM books WHERE id = ?', [id]);
  return rows[0];
};

export const create = async (data) => {
  const { isbn, title, author, publication_year, genre } = data;
  const [result] = await pool.query(
    'INSERT INTO books (isbn, title, author, publication_year, genre) VALUES (?, ?, ?, ?, ?)',
    [isbn, title, author, publication_year, genre]
  );
  return result.insertId;
};

export const update = async (id, data) => {
  const { isbn, title, author, publication_year, genre } = data;
  const [result] = await pool.query(
    'UPDATE books SET isbn = ?, title = ?, author = ?, publication_year = ?, genre = ? WHERE id = ?',
    [isbn, title, author, publication_year, genre, id]
  );
  return result.affectedRows;
};

export const remove = async (id) => {
  const [result] = await pool.query('DELETE FROM books WHERE id = ?', [id]);
  return result.affectedRows;
};
```

### 4. `controllers/bookController.js`
```javascript
import * as BookModel from '../models/bookModel.js';

export const getBooks = async (req, res) => {
  try {
    const books = await BookModel.findAll();
    res.json({ success: true, message: 'Books retrieved', data: books });
  } catch (err) {
    res.status(500).json({ success: false, message: 'Server error', error: err.message });
  }
};

export const getBook = async (req, res) => {
  try {
    const book = await BookModel.findById(req.params.id);
    if (!book) return res.status(404).json({ success: false, message: 'Book not found' });
    res.json({ success: true, message: 'Book details retrieved', data: book });
  } catch (err) {
    res.status(500).json({ success: false, message: 'Server error', error: err.message });
  }
};

export const createBook = async (req, res) => {
  try {
    const id = await BookModel.create(req.body);
    res.status(201).json({ success: true, message: 'Book added', data: { id, ...req.body } });
  } catch (err) {
    res.status(400).json({ success: false, message: 'Could not create book', error: err.message });
  }
};
```

---

## Postman Test Guide
1. **GET Books:** Send `GET http://localhost:5000/api/books`
2. **POST Book:** Send `POST http://localhost:5000/api/books` with Body:
   ```json
   {
     "isbn": "978-0131103627",
     "title": "The C Programming Language",
     "author": "Brian W. Kernighan",
     "publication_year": 1988,
     "genre": "Computer Science"
   }
   ```
