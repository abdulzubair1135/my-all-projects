# Referential Actions: `ON DELETE` & `ON UPDATE` (CASCADE, SET NULL, RESTRICT)

## 1. What are Referential Actions?
Referential actions define what happens to child table records when a referenced parent record is deleted or updated.

---

## 2. Common Referential Action Options

| Option | Behavior on Delete/Update of Parent Row |
|--------|------------------------------------------|
| **`CASCADE`** | Deletes/updates corresponding rows in child table automatically |
| **`SET NULL`** | Sets foreign key column in child table to `NULL` |
| **`RESTRICT` / `NO ACTION`** | Rejects delete/update operation on parent row (Default behavior) |

---

## 3. SQL Examples

### ON DELETE CASCADE Example:
When a department is deleted, all students enrolled in that department are automatically deleted.
```sql
CREATE TABLE students (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    department_id INT,
    FOREIGN KEY (department_id) REFERENCES departments(id) 
        ON DELETE CASCADE 
        ON UPDATE CASCADE
);
```

### ON DELETE SET NULL Example:
When a manager is deleted, employee's `manager_id` foreign key is set to `NULL`.
```sql
CREATE TABLE employees (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    manager_id INT NULL,
    FOREIGN KEY (manager_id) REFERENCES employees(id) 
        ON DELETE SET NULL
);
```
