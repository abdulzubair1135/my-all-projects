# Transactions Viva & Exam Questions Guide

## Question 1: What is a Database Transaction and why is it important?
- **Answer**: A database transaction is a sequence of SQL operations executed as a single logical unit of work. It ensures data consistency and integrity, guaranteeing that either all operations succeed (`COMMIT`) or none of them apply (`ROLLBACK`).

---

## Question 2: Explain ACID properties with real-world examples.
- **Answer**:
  - **Atomicity**: Entire bank payment finishes, or no money is deducted at all.
  - **Consistency**: Account balance cannot drop below \$0 if constrained.
  - **Isolation**: Concurrent flight seat bookings do not double-book the same seat.
  - **Durability**: System crash immediately after transaction commit does not erase the saved record.

---

## Question 3: What is the difference between `connection.query()` and `connection.beginTransaction()` in `mysql2`?
- **Answer**:
  - `pool.query()` picks an arbitrary connection from the pool for a single isolated query and immediately returns it.
  - `pool.getConnection()` locks a dedicated connection. Calling `connection.beginTransaction()` disables autocommit on that connection until `connection.commit()` or `connection.rollback()` is invoked.

---

## Question 4: Why must `connection.release()` be placed inside a `finally` block?
- **Answer**: Because if an error occurs inside `try` block, execution jumps to `catch`. If `release()` is outside `finally`, the database connection remains locked open forever, eventually causing pool exhaustion (`Error: Connection pool exhausted`).
