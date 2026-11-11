# Step 01: Question Paper Reading & Analysis (BCA Exam Flow)

Exam me Question Paper surface level se drag/read nahi karna. Structure follow karo step-by-step:

---

## 1. Exam Problem Statement Read Strategy
- **First Pass (1 minute):** High-level view scalar karo ki project ka doman kya hai (e.g., Student Management, Library, POS System, Auth System).
- **Second Pass (2-3 minutes):** Core entities aur features underline/highlight karo (e.g., Register, Login, CRUD items, Generate Bill).
- **Third Pass (1 minute):** Technical constraints note karo (e.g., MySQL table structure, validation fields, JWT Token required, specific response format).

---

## 2. Keywords Table (Question to Action Mapping)

| Keyword in Question Paper | What it Means Technical Side | Code/File to Implement |
| :--- | :--- | :--- |
| "Create API for user registration" | User create in DB with hashed password | Auth controller, Password Hash helper, Validation rules |
| "Authenticate user / Login" | Validate credentials & generate JWT token | Auth controller, JWT sign helper, Auth middleware |
| "Protected route / Admin only" | Verification of Bearer token & role check | Auth Middleware (`authMiddleware`) |
| "Perform CRUD operations on Product" | Create, Read (All/ByID), Update, Delete | Product Model, Controller, Express Routes |
| "Generate Invoice / Calculate Total" | Calculate item total, insert into Bills | Transaction / Bill Controller & Bill Model |
| "Return appropriate JSON response" | Standard response `{ success, message, data }` | `response.js` utility helper |

---

## 3. Quick Mindset Rules for BCA Practical Exam
1. **Never jump directly to writing code** without reading all requirements!
2. **Database First Rule:** SQL table schema and fields logic fixed karo pehle.
3. **Keep structure clean:** Always divide into `config`, `models`, `controllers`, `routes`, `middleware`, `validation`.
4. **Use ES Modules (`import/export`):** Set `"type": "module"` in `package.json`.
5. **Always test in Postman or Curl:** Verify output matches standard JSON response.
