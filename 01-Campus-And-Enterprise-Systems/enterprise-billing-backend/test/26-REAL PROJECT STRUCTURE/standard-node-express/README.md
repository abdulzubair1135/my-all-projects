# Standard Node.js & Express Project Architecture

## Overview
The standard structure used for basic REST APIs and single-entity applications in BCA practical exams.

---

## Directory Diagram

```
standard-node-express/
├── .env
├── .gitignore
├── package.json
├── README.md
├── server.js
├── config/
│   └── db.js
├── controllers/
│   └── itemController.js
├── routes/
│   └── itemRoutes.js
└── sql/
    └── schema.sql
```

---

## Component Explanation
- `server.js`: Application entry point initializing Express, middleware, and server port.
- `config/db.js`: Database connection pool instantiation using `mysql2/promise`.
- `controllers/`: Handles request processing and query execution.
- `routes/`: Express router definitions connecting paths to controllers.
