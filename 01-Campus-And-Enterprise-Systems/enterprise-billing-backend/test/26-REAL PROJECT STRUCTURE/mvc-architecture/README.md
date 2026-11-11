# MVC Architecture Blueprint

## Overview
Model-View-Controller architecture splits concerns into data management (Model/DB), logic execution (Controller), and HTTP routing (Routes).

---

## Directory Diagram

```
mvc-architecture/
├── .env
├── package.json
├── server.js
├── config/
│   └── db.js
├── models/
│   ├── productModel.js
│   └── userModel.js
├── controllers/
│   ├── productController.js
│   └── userController.js
├── routes/
│   ├── productRoutes.js
│   └── userRoutes.js
└── middleware/
    ├── authMiddleware.js
    └── errorMiddleware.js
```

---

## Data Flow Diagram
`HTTP Request` -> `Routes` -> `Middleware` -> `Controller` -> `Model/DB Query` -> `JSON Response`
