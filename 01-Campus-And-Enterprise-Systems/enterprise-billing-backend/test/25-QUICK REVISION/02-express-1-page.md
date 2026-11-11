# Express.js One-Page Quick Revision Sheet

## What is Express.js?
Express.js is a minimal, flexible Node.js web application framework providing a robust set of features for web and mobile applications, specialized in building RESTful APIs.

---

## Minimal Server Skeleton
```javascript
import express from 'express';
const app = express();

app.use(express.json()); // Middleware to parse JSON body

app.get('/api/health', (req, res) => {
    res.json({ success: true, message: 'API healthy' });
});

app.listen(5000, () => console.log('Server running on port 5000'));
```

---

## Express Routing Methods
- `app.get(path, handler)`: Read data
- `app.post(path, handler)`: Create new resource
- `app.put(path, handler)`: Update whole resource
- `app.patch(path, handler)`: Update partial resource
- `app.delete(path, handler)`: Remove resource

---

## Request Object Properties (`req`)
- `req.body`: Parsed request body payload (Requires `express.json()`)
- `req.params`: URL path parameters (e.g. `/api/users/:id` -> `req.params.id`)
- `req.query`: URL query parameters (e.g. `?search=mouse` -> `req.query.search`)
- `req.headers`: HTTP request headers (e.g. `req.headers['authorization']`)
