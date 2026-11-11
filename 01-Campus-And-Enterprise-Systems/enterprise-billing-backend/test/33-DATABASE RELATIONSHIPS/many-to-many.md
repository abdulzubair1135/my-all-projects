# Database Relationships: Many-to-Many (M:N)

## 1. What is a Many-to-Many Relationship?
A Many-to-Many (M:N) relationship occurs when multiple records in Table A are associated with multiple records in Table B.

---

## 2. Real-World Use Case Example
- A `Student` can enroll in multiple `Courses`.
- A `Course` can have multiple enrolled `Students`.

---

## 3. Junction / Pivot Table Rule
Relational databases (like MySQL) cannot directly create a foreign key link for M:N relationships. We must break a Many-to-Many relationship down into **two 1:N relationships** using an intermediate **Junction Table** (also known as a Pivot or Bridge Table).

---

## 4. SQL Implementation Schema

```sql
-- Table A: Students
CREATE TABLE students (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL
);

-- Table B: Courses
CREATE TABLE courses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(100) NOT NULL
);

-- Junction Table: enrollments
CREATE TABLE enrollments (
    student_id INT NOT NULL,
    course_id INT NOT NULL,
    enrolled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (student_id, course_id), -- Composite Primary Key
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE
);
```
