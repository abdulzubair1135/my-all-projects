# Node.js One-Page Quick Revision Sheet

## What is Node.js?
Node.js is an open-source, cross-platform JavaScript runtime built on Chrome's V8 engine that enables running JavaScript on the server side using an asynchronous, event-driven I/O model.

---

## Core Concepts for Practical Exams

### 1. Asynchronous non-blocking I/O
- Node.js uses a single thread for event loop processing while offloading I/O operations (file system, database queries) to libuv worker pool.

### 2. Standard ES Module Import/Export
```javascript
// Exporting:
export const greet = (name) => `Hello ${name}`;
export default greet;

// Importing:
import greet from './greet.js';
```

### 3. Core Modules Cheat Sheet
- `fs/promises`: File system operations using promises.
- `path`: Working with file and directory paths.
- `http`: Native web server creation.

---

## Key Exam Command Line Commands
```bash
npm init -y                  # Initialize package.json
npm install express mysql2   # Install dependencies
node server.js               # Run server
```
