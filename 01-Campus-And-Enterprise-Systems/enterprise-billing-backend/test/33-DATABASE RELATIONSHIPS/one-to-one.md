# Database Relationships: One-to-One (1:1)

## 1. What is a One-to-One Relationship?
A One-to-One (1:1) relationship means that a single record in Table A is associated with exactly one record in Table B, and vice versa.

---

## 2. Real-World Use Case Example
- A `User` has exactly one `Passport` detail.
- A `Student` has exactly one `StudentProfileDetail` (e.g. bio, medical notes, emergency contact).

---

## 3. SQL Implementation Schema

```sql
-- Main Users Table
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE
);

-- Profile Details Table (One-to-One linked via UNIQUE Foreign Key)
CREATE TABLE user_profiles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL UNIQUE, -- UNIQUE constraint enforces 1:1!
    address TEXT,
    phone VARCHAR(15),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
```

---

## 4. Key Exam Tip
To enforce a true 1:1 relationship in SQL, the foreign key column (`user_id`) MUST have a **`UNIQUE`** constraint. Without `UNIQUE`, it would default to a One-to-Many relationship.
