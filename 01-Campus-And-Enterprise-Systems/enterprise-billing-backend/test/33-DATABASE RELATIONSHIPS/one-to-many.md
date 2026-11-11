# Database Relationships: One-to-Many (1:N)

## 1. What is a One-to-Many Relationship?
A One-to-Many (1:N) relationship occurs when a single record in Table A can be linked to one or multiple records in Table B, but a record in Table B belongs to only one record in Table A. This is the most common database relationship.

---

## 2. Real-World Use Case Example
- One `Department` has many `Students`.
- One `Customer` places many `Orders`.
- One `Author` writes many `Books`.

---

## 3. SQL Implementation Schema

```sql
-- Parent Table (1 side)
CREATE TABLE departments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    dept_name VARCHAR(100) NOT NULL
);

-- Child Table (N side holds foreign key)
CREATE TABLE students (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    department_id INT NOT NULL, -- Foreign Key referencing departments.id
    FOREIGN KEY (department_id) REFERENCES departments(id)
);
```

---

## 4. Query Example
```sql
SELECT d.dept_name, s.name 
FROM departments d
INNER JOIN students s ON d.id = s.department_id
WHERE d.id = 1;
```
