# Express Route Parameters & Query Handling Guide (`route-params.md`)

Express provides flexible options to extract request parameters from URLs:

---

## 1. Parameter Types Comparison

| Parameter Location | Express Object | Example URL Pattern | Purpose |
| :--- | :--- | :--- | :--- |
| **Path Parameter** | `req.params` | `/api/students/:id` | Unique entity identifier segment |
| **Query Parameter** | `req.query` | `/api/students?page=1&sort=asc` | Filtering, search, pagination |
| **Request Body** | `req.body` | `POST /api/students` (JSON) | Resource payload data creation |

---

## 2. Optional Route Parameters & Regex Matching

```javascript
import express from 'express';
const router = express.Router();

// Optional Parameter with ?
router.get('/reports/:year?', (req, res) => {
  const year = req.params.year || new Date().getFullYear();
  res.json({ success: true, year });
});

// Regex Constraint: Match only numeric ID parameters
router.get('/users/:id(\\d+)', (req, res) => {
  res.json({ success: true, id: req.params.id });
});
```

---

## 3. Nested Routing with `mergeParams: true`

When splitting nested routes across separate module files, pass `{ mergeParams: true }` to `express.Router()`:

```javascript
// server.js or main router
import courseRoutes from './routes/course.routes.js';
import nestedStudentRoutes from './routes/nested.routes.js';

// Parent Router
app.use('/api/courses/:courseId/students', nestedStudentRoutes);
```

```javascript
// nested.routes.js
import express from 'express';
const router = express.Router({ mergeParams: true }); // Retains :courseId from parent URL

router.get('/', (req, res) => {
  const courseId = req.params.courseId; // Accessible!
  res.json({ courseId });
});
```
