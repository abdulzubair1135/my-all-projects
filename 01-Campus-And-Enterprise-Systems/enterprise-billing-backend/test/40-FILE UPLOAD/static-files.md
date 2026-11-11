# Serving Static Uploaded Files in Express (`static-files.md`)

Once files (such as images, PDFs, avatars) are saved to the server's filesystem, Express requires static file middleware (`express.static`) to serve them directly via standard HTTP URLs.

---

## 1. Configuring Static File Middleware

Use `express.static()` built-in middleware in your main `server.js`:

```javascript
import express from 'express';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();

// Serve the 'uploads' folder statically under the '/uploads' virtual path prefix
app.use('/uploads', express.static(path.join(__dirname, 'uploads')));
```

---

## 2. Accessing Uploaded Files via Browser / Client

If a file is saved at filesystem path `uploads/avatar-12345.png`:
- Server URL: `http://localhost:5000/uploads/avatar-12345.png`

---

## 3. Database Storage Best Practice

> [!IMPORTANT]
> Never store binary image/file data directly in MySQL BLOB columns if avoidable. Store the **relative file URL string** (e.g. `/uploads/avatar-12345.png`) in MySQL instead.

### Example MySQL Table Schema
```sql
CREATE TABLE users (
  id INT PRIMARY KEY AUTO_INCREMENT,
  name VARCHAR(100) NOT NULL,
  email VARCHAR(100) UNIQUE NOT NULL,
  profile_pic VARCHAR(255) DEFAULT '/uploads/default-avatar.png',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```
