# Complete Exam Blueprint & Roadmap

Complete Roadmap from blank directory to 100% finished backend project in BCA Practical Exam.

---

## Time Allocation Guide (3 Hours Exam)

| Time Slot | Phase | Tasks |
| :--- | :--- | :--- |
| **00:00 - 00:15** | Setup & DB Schema | Create folder, `npm init -y`, install dependencies, run SQL commands in MySQL |
| **00:15 - 00:30** | Database & Config | Create `config/db.js`, `.env`, helper response functions |
| **00:30 - 01:15** | Auth System | Implement Password Hash, JWT helpers, User Model, Auth Controllers & Middleware |
| **01:15 - 02:15** | Core CRUD & Business Logic | Build Product/Franchise/Bill Models, Validation, Controllers, Routes |
| **02:15 - 02:45** | Postman Testing | Test Register, Login, Token Header, CRUD endpoints, and record screenshots/json |
| **02:45 - 03:00** | Final Check & Documentation | Fill README.md, check `.env.example`, ensure server launches without errors |

---

## Gold Rules to Remember in Exam
1. Always use ES Modules (`import`/`export`) as project specifies `"type": "module"`.
2. Parameterize SQL queries: `pool.query('SELECT * FROM users WHERE id = ?', [id])`.
3. Standard JSON Response: `{ success: true/false, message: "...", data/error: ... }`.
4. Wrap async controllers in `try...catch` and pass errors to `next(err)`.
