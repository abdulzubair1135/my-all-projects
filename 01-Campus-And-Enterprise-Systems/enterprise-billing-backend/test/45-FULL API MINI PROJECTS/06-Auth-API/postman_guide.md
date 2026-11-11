# Postman Guide - Auth API

1. **Register User**
   - `POST http://localhost:5000/api/auth/register`
   - Body: `{ "name": "Admin User", "email": "admin@example.com", "password": "password123", "role": "admin" }`

2. **Login**
   - `POST http://localhost:5000/api/auth/login`
   - Body: `{ "email": "admin@example.com", "password": "password123" }`
   - Save the returned JWT token.

3. **Get Profile (Protected)**
   - `GET http://localhost:5000/api/auth/profile`
   - Header: `Authorization: Bearer <token>`
