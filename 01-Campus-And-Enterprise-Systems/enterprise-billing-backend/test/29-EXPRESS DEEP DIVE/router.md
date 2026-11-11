# Express `express.Router()` Guide

## 1. What is `express.Router`?
An `express.Router` instance is a complete middleware and routing system; it is often referred to as a "mini-app". It helps organize large Express applications by grouping routes into modular files.

---

## 2. Typical Modular Folder Structure
```
project-root/
  ├── routes/
  │   ├── studentRoutes.js
  │   └── courseRoutes.js
  └── server.js
```

---

## 3. Implementation Example (ES Modules)

### File: `routes/studentRoutes.js`
```js
import express from 'express';

const router = express.Router();

// Mount routes relative to prefix
router.get('/', (req, res) => {
  res.status(200).json({ success: true, message: "List of all students" });
});

router.get('/:id', (req, res) => {
  const { id } = req.params;
  res.status(200).json({ success: true, data: { id, name: "Student " + id } });
});

router.post('/', (req, res) => {
  const { name } = req.body;
  res.status(201).json({ success: true, message: "Student created", data: { id: 99, name } });
});

export default router;
```

### File: `server.js`
```js
import express from 'express';
import studentRoutes from './routes/studentRoutes.js';

const app = express();
app.use(express.json());

// Mounting router with prefix /api/students
app.use('/api/students', studentRoutes);

app.listen(5000, () => console.log('Server started on port 5000'));
```

---

## 4. Advantages for Exams
- **Modularity**: Keeps `server.js` clean and manageable.
- **Separation of Concerns**: Allows different developers to work on separate entity routes.
- **Reusable Middlewares**: Middlewares can be applied specifically to a router instance using `router.use(authMiddleware)`.
