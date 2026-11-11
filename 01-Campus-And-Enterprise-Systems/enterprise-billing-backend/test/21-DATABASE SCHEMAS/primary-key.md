# Primary Key Guide for Backend Exams

## What is a Primary Key?
A **Primary Key (PK)** is a column or set of columns in a database table that uniquely identifies each row (record) in that table.

### Key Characteristics:
1. **Uniqueness**: Every value in the primary key column must be distinct (no duplicate values allowed).
2. **NOT NULL constraint**: A primary key column cannot contain `NULL` values.
3. **Single per table**: A table can have only one Primary Key constraint (which can be composed of one or multiple columns).

---

## SQL Syntax Examples

### 1. Single Column Primary Key (Standard Exam Pattern)
```sql
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE
);
```

### 2. Composite Primary Key (Multi-Column)
Used when a unique record is determined by a combination of two or more columns (e.g., mapping tables).
```sql
CREATE TABLE student_courses (
    student_id INT NOT NULL,
    course_id INT NOT NULL,
    enrolled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (student_id, course_id)
);
```

---

## Exam Tips for Primary Keys
- Always use `id INT AUTO_INCREMENT PRIMARY KEY` for standard entity tables (`users`, `products`, `customers`).
- Place `PRIMARY KEY` at the very beginning of table definition so your schema structure stays clean and readable for external examiners.
- `AUTO_INCREMENT` automatically generates numbers `1, 2, 3...` when inserting records without passing `id` explicitly.
