# Express.js Routing Deep Dive

## 1. What is Routing?
Routing refers to determining how an application responds to a client request to a particular endpoint, which is a URI (or path) and a specific HTTP request method (`GET`, `POST`, `PUT`, `DELETE`, etc.).

---

## 2. Basic Route Structure
```js
app.METHOD(PATH, HANDLER)
```
- `app`: Instance of Express (`const app = express()`).
- `METHOD`: Lowercase HTTP method (e.g., `get`, `post`, `put`, `delete`).
- `PATH`: Path on the server (e.g., `/api/students`).
- `HANDLER`: Callback function executed when route matches `(req, res) => {}`.

---

## 3. Code Example (ES Modules)

```js
import express from 'express';

const app = express();
app.use(express.json());

// Root route
app.get('/', (req, res) => {
  res.status(200).json({ success: true, message: "Welcome to Express Server" });
});

// Resource routes
app.get('/api/products', (req, res) => {
  res.status(200).json({ success: true, data: [] });
});

app.post('/api/products', (req, res) => {
  const { title, price } = req.body;
  res.status(201).json({ success: true, message: "Product added", data: { id: 1, title, price } });
});

// Chained route handlers with app.route()
app.route('/api/articles')
  .get((req, res) => {
    res.json({ success: true, message: "Fetch all articles" });
  })
  .post((req, res) => {
    res.json({ success: true, message: "Article created" });
  });

app.listen(5000, () => console.log('Server running on port 5000'));
```

---

## 4. Exam Key Concepts
- **Matching Order**: Express checks routes sequentially from top to bottom. Order of registration matters!
- **Wildcard Route / 404 Handler**: Placed at the bottom after all defined routes.
