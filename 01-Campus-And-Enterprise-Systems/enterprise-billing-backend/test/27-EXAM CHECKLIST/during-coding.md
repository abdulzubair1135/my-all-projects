# During Coding Checklist

## Development & Code Quality Checklist

- [ ] **Import File Extensions**: Include `.js` extension in all local relative imports (e.g. `import pool from './config/db.js'`).
- [ ] **Middleware Registration Order**: Place `app.use(express.json())` and `app.use(cors())` *before* mounting API routes in `server.js`.
- [ ] **Parameterized SQL Queries**: Use `pool.query('SELECT * FROM table WHERE id = ?', [id])` to prevent SQL Injection and syntax errors.
- [ ] **Async / Await Error Handling**: Wrap all controller database operations inside `try...catch` blocks.
- [ ] **Array Destructuring**: Destructure `[rows]` from `await pool.query(...)` calls.
- [ ] **Express Validator Check**: Ensure `validationResult(req)` is invoked to intercept invalid payloads.
- [ ] **Standardized Response Format**: Return JSON with `{ success: true/false, message: "...", data: ... }`.
- [ ] **HTTP Status Codes**: Set `200` (OK), `201` (Created), `400` (Validation), `401` (Unauthorized), `404` (Not Found), `500` (Server Error).
