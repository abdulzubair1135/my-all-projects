# Top 10 Exam Mistakes & How to Avoid Them

## 1. Missing `.js` extension in ES Modules imports
- **Mistake**: `import db from './config/db';`
- **Fix**: `import db from './config/db.js';`

## 2. Missing `app.use(express.json())`
- **Mistake**: Accessing `req.body` returns `undefined`.
- **Fix**: Add `app.use(express.json())` at top of `server.js` before routes.

## 3. Storing plain text passwords in Database
- **Mistake**: Inserting `req.body.password` directly into SQL query.
- **Fix**: Use `const hashed = await bcrypt.hash(password, 10);`.

## 4. Unhandled Promise Rejections
- **Mistake**: Database error crashes server because `try...catch` is missing.
- **Fix**: Always wrap async controller logic in `try...catch` blocks.

## 5. SQL Injection & String Formatting Errors
- **Mistake**: Query string interpolation `` `SELECT * FROM users WHERE name = '${name}'` ``.
- **Fix**: Use parameterized queries `pool.query('SELECT * FROM users WHERE name = ?', [name])`.

## 6. Port EADDRINUSE Conflict
- **Mistake**: Running two instances of `node server.js` simultaneously.
- **Fix**: Kill previous process or change `PORT` in `.env`.

## 7. Not Releasing MySQL Transaction Connection
- **Mistake**: Connection pool exhausted because `conn.release()` was missing in `finally` block.
- **Fix**: Always call `conn.release()` inside `finally`.

## 8. Misconfigured Cors Middleware
- **Mistake**: Registering `app.use(cors())` after defining API routes.
- **Fix**: Place `cors()` middleware before any route registrations.

## 9. Forgetting `validationResult(req)`
- **Mistake**: Adding validation array to route without checking `validationResult(req)` in middleware/controller.
- **Fix**: Intercept errors with `const errors = validationResult(req); if (!errors.isEmpty()) return res.status(400)...`.

## 10. Trailing Commas in Postman JSON Body
- **Mistake**: Postman returns parsing error due to trailing comma in request payload.
- **Fix**: Remove trailing commas in JSON object properties.
