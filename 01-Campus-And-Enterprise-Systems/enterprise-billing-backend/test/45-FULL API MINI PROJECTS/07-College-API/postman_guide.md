# Postman Guide - College API

1. `GET /api/departments` - List departments
2. `GET /api/courses` - List courses with department details (SQL JOIN)
3. `GET /api/courses/1` - Get single course detail with department
4. `POST /api/courses` - Add new course
   Body: `{ "course_code": "CS103", "course_name": "Database Management Systems", "credits": 4, "department_id": 1 }`
