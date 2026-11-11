# RESTful API Naming Conventions & Best Practices

## 1. Golden Rules for API Endpoints

1. **Use Nouns (Plural), Not Verbs**:
   - ❌ Bad: `/api/getStudents`, `/api/createStudent`, `/api/deleteUser`
   - ✅ Good: `GET /api/students`, `POST /api/students`, `DELETE /api/users/:id`

2. **Use Lowercase with Hyphens (kebab-case)**:
   - ❌ Bad: `/api/userProfiles`, `/api/user_profiles`
   - ✅ Good: `/api/user-profiles`

3. **Nest Hierarchical Resources**:
   - Get all orders for student ID 5: `GET /api/students/5/orders`
   - Get specific order 10 for student ID 5: `GET /api/students/5/orders/10`

4. **Use Query Parameters for Filtering, Sorting, & Pagination**:
   - Filtering: `GET /api/students?course=BCA`
   - Sorting: `GET /api/students?sort=name&order=asc`
   - Pagination: `GET /api/students?page=1&limit=10`

---

## 2. API Endpoint Cheatsheet Table

| Goal | Method | URL Path | HTTP Status Code |
|------|--------|----------|------------------|
| Fetch all books | `GET` | `/api/books` | 200 OK |
| Fetch book by ID | `GET` | `/api/books/12` | 200 OK |
| Add new book | `POST` | `/api/books` | 201 Created |
| Update book 12 | `PUT` | `/api/books/12` | 200 OK |
| Delete book 12 | `DELETE` | `/api/books/12` | 200 OK / 204 No Content |
| Search books | `GET` | `/api/books?search=express` | 200 OK |

---

## 3. Exam Tips & Common Viva Questions
- **Q**: Is `/api/updateUser/5` RESTful? Why or why not?
  - **A**: No, because it uses a verb (`updateUser`) in the URL. REST uses standard HTTP methods (`PUT` or `PATCH`) with noun endpoints (`/api/users/5`) to indicate action.
