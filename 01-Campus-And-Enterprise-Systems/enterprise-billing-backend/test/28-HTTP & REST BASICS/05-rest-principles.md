# REST Principles Guide (Representational State Transfer)

## 1. What is REST?
REST stands for **Representational State Transfer**. It is an architectural style for designing networked applications and web services that use stateless, client-server, cacheable communications protocols (primarily HTTP).

---

## 2. Six Core Guiding Principles of REST

1. **Client-Server Architecture**:
   - UI and data storage are decoupled. Client manages UI/UX; Server handles database and business logic.
2. **Statelessness**:
   - Each HTTP request from client must contain all necessary information (e.g., Auth tokens). Server stores no client session context between requests.
3. **Cacheability**:
   - Responses must explicitly define themselves as cacheable or non-cacheable to improve client efficiency.
4. **Uniform Interface**:
   - Resources are uniquely identified using URIs. Standard HTTP methods (GET, POST, PUT, DELETE) are used.
5. **Layered System**:
   - Client cannot ordinarily tell whether it is connected directly to the end server or an intermediate proxy/load balancer.
6. **Code on Demand (Optional)**:
   - Servers can temporarily extend client functionality by transferring executable code (e.g., JavaScript).

---

## 3. CRUD to REST Method Mapping

| CRUD Operation | SQL Keyword | REST HTTP Method | Example Endpoint |
|----------------|-------------|------------------|------------------|
| **Create** | `INSERT` | `POST` | `POST /api/students` |
| **Read** | `SELECT` | `GET` | `GET /api/students` |
| **Read Single**| `SELECT ... WHERE` | `GET` | `GET /api/students/:id` |
| **Update** | `UPDATE` | `PUT` / `PATCH` | `PUT /api/students/:id` |
| **Delete** | `DELETE` | `DELETE` | `DELETE /api/students/:id` |

---

## 4. Key Exam Definitions
- **Resource**: Any entity or business object exposed via URI (e.g., student, product, order).
- **Stateless Server**: Server does not store session variables (like `req.session.user`) on server memory across requests; tokens (JWT) are sent in each header instead.
