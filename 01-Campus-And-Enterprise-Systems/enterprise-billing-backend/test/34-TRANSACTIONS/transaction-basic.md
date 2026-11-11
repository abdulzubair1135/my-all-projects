# Database Transactions & ACID Properties Guide

## 1. What is a Database Transaction?
A transaction is a single logical unit of work that performs one or more database operations (such as inserts, updates, deletes). A transaction must execute completely or not at all (All-or-Nothing principle).

---

## 2. ACID Properties (High Exam Priority)

| Property | Full Name | Explanation |
|----------|-----------|-------------|
| **A** | **Atomicity** | All operations in transaction succeed together, or all fail and roll back. |
| **C** | **Consistency** | Database moves from one valid state to another, respecting constraints. |
| **I** | **Isolation** | Concurrent transactions execute independently without interfering with each other. |
| **D** | **Durability** | Committed changes are permanently saved in persistent storage, even during system crashes. |

---

## 3. Real-World Bank Transfer Scenario
Transferring \$100 from Account A to Account B requires two updates:
1. Deduct \$100 from Account A: `UPDATE accounts SET balance = balance - 100 WHERE id = A;`
2. Add \$100 to Account B: `UPDATE accounts SET balance = balance + 100 WHERE id = B;`

If step 1 succeeds but server loses power before step 2, the money disappears! Transactions ensure both steps complete together via `COMMIT`, or if step 2 fails, step 1 is reversed via `ROLLBACK`.
