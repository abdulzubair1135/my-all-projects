# Step 08: Postman Testing & Verification Flow

Exam evaluator ke samne project test karke dikhane ke liye Postman setup clear hona chahiye.

---

## 1. Setup Steps in Postman
1. Create New Collection (e.g. `BCA-Exam-API`).
2. Add Environment Variables (optional, e.g. `baseUrl = http://localhost:5000/api`, `token = eyJhbG...`).

---

## 2. Test Execution Order
1. **Health Check:** `GET http://localhost:5000/api/health` -> verify server running.
2. **Register:** `POST http://localhost:5000/api/auth/register`
   - Body: `raw -> JSON`
   - Test response contains `success: true`.
3. **Login:** `POST http://localhost:5000/api/auth/login`
   - Copy token from response `data.token`.
4. **Protected Route Test:**
   - Headers: `Authorization: Bearer <JWT_TOKEN>`
   - `GET http://localhost:5000/api/auth/me`
5. **CRUD Operations Test:**
   - `POST /api/products` (Create)
   - `GET /api/products` (Read All)
   - `GET /api/products/1` (Read Single)
   - `PUT /api/products/1` (Update)
   - `DELETE /api/products/1` (Delete)

---

## 3. Postman Export for Exam Submission
- Export collection as **Postman Collection v2.1 (JSON)**.
- Save inside `09-Postman/` directory of your project folder.
