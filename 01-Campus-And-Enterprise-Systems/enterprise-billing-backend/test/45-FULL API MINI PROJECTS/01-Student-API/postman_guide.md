# Postman Testing Guide - Student API

## Endpoints

### 1. Get All Students
- **Method:** `GET`
- **URL:** `http://localhost:5000/api/students`

### 2. Get Student By ID
- **Method:** `GET`
- **URL:** `http://localhost:5000/api/students/1`

### 3. Create Student
- **Method:** `POST`
- **URL:** `http://localhost:5000/api/students`
- **Headers:** `Content-Type: application/json`
- **Body (JSON):**
```json
{
  "roll_no": "BCA104",
  "name": "Suresh Verma",
  "email": "suresh@example.com",
  "department": "Computer Applications",
  "gpa": 8.75
}
```

### 4. Update Student
- **Method:** `PUT`
- **URL:** `http://localhost:5000/api/students/1`
- **Headers:** `Content-Type: application/json`
- **Body (JSON):**
```json
{
  "roll_no": "BCA101",
  "name": "Rahul Sharma updated",
  "email": "rahul.new@example.com",
  "department": "Computer Science",
  "gpa": 8.90
}
```

### 5. Delete Student
- **Method:** `DELETE`
- **URL:** `http://localhost:5000/api/students/1`
