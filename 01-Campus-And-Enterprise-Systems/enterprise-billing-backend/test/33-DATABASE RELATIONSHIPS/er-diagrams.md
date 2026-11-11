# Entity-Relationship (ER) Diagrams & Database Design Guide

## 1. What is an ER Diagram?
An Entity-Relationship (ER) Diagram is a visual representation of entities (tables), attributes (columns), and their relationships (keys) in a database.

---

## 2. Key Symbols & Notations
- **Entity (Rectangle)**: Database table (e.g. `Student`, `Department`).
- **Attribute (Oval)**: Properties/Columns of entity (e.g. `name`, `email`).
- **Key Attribute (Underlined Oval)**: Primary key (e.g. `<u>student_id</u>`).
- **Relationship (Diamond)**: Association between entities (e.g. `Enrolls In`, `Belongs To`).

---

## 3. Visual Relationship Diagram (Mermaid)

```mermaid
erDiagram
    DEPARTMENT ||--o{ STUDENT : "belongs to"
    STUDENT ||--o{ ENROLLMENT : "has"
    COURSE ||--o{ ENROLLMENT : "contains"
    USER ||--|| PROFILE : "has profile"

    DEPARTMENT {
        int id PK
        string dept_name
    }

    STUDENT {
        int id PK
        string name
        string email
        int department_id FK
    }

    COURSE {
        int id PK
        string title
    }

    ENROLLMENT {
        int student_id PK,FK
        int course_id PK,FK
        date enrolled_at
    }

    USER {
        int id PK
        string username
    }

    PROFILE {
        int id PK
        int user_id FK,UK
        string address
    }
```
