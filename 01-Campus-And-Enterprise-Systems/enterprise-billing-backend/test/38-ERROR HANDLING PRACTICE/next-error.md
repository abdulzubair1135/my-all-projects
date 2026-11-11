# Express `next(err)` and Central Error Middleware (`next-error.md`)

In Express.js, the `next()` function serves two distinct purposes depending on whether an argument is passed to it:

1. **`next()` without arguments**: Passes control to the next normal route handler/middleware in the stack.
2. **`next(err)` with an argument**: Skips all remaining normal middlewares and jumps straight to Express's central error-handling middleware.

---

## 1. How Express Recognizes Central Error Middleware

Express identifies error-handling middleware by its function signature having **exactly 4 parameters**:

```javascript
// MUST have 4 arguments: (err, req, res, next)
app.use((err, req, res, next) => {
  console.error('Central Error Handler Caught:', err);

  const statusCode = err.statusCode || 500;
  const message = err.message || 'Internal Server Error';

  res.status(statusCode).json({
    success: false,
    message,
    error: process.env.NODE_ENV === 'development' ? err.stack : undefined
  });
});
```

> [!WARNING]
> If you omit any parameter (e.g. `(err, req, res)` with only 3 params), Express treats it as a normal middleware and will not receive errors from `next(err)`.

---

## 2. Custom App Error Class

Creating a custom error class allows throwing specific HTTP status codes cleanly:

```javascript
// utils/AppError.js
export class AppError extends Error {
  constructor(message, statusCode) {
    super(message);
    this.statusCode = statusCode;
    this.status = `${statusCode}`.startsWith('4') ? 'fail' : 'error';
    this.isOperational = true; // Flag for operational error vs application bug

    Error.captureStackTrace(this, this.constructor);
  }
}
```

### Throwing AppError in Controllers:
```javascript
import { AppError } from '../utils/AppError.js';

export const getStudentProfile = async (req, res, next) => {
  try {
    const student = await findStudent(req.params.id);
    if (!student) {
      // Passes custom error with HTTP 404 status code
      return next(new AppError('Student profile not found', 404));
    }
    res.json({ success: true, data: student });
  } catch (err) {
    next(err);
  }
};
```

---

## 3. Position in `server.js`

Error middleware MUST be mounted **AFTER** all application routes and custom middlewares, but **BEFORE** `app.listen()`:

```javascript
import express from 'express';
import studentRoutes from './routes/student.routes.js';
import { errorMiddleware } from './middleware/error.middleware.js';

const app = express();
app.use(express.json());

// 1. Application Routes
app.use('/api/students', studentRoutes);

// 2. 404 Handler for undefined routes
app.use((req, res, next) => {
  res.status(404).json({
    success: false,
    message: `Cannot find endpoint ${req.originalUrl} on this server`
  });
});

// 3. Central Error Middleware (ALWAYS LAST)
app.use(errorMiddleware);

app.listen(5000, () => console.log('Server running on port 5000'));
```
