# MVC Architecture One-Page Quick Revision Sheet

## What is MVC?
**MVC (Model-View-Controller)** separates application logic into three main interconnected components:

1. **Model (`models/` or `config/db.js`)**: Database schemas, queries, and data structures.
2. **Controller (`controllers/`)**: Business logic, handles requests, calls models, returns responses.
3. **View**: In REST APIs, the View layer is replaced by formatted **JSON responses**.
4. **Routes (`routes/`)**: Maps HTTP URLs and methods to specific Controller functions.

---

## Directory Folder Structure Blueprint
```
project/
├── config/
│   └── db.js
├── controllers/
│   └── productController.js
├── middleware/
│   └── authMiddleware.js
├── routes/
│   └── productRoutes.js
├── .env
├── package.json
└── server.js
```
