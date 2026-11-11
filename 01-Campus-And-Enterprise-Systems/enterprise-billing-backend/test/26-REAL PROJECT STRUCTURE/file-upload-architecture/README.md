# File Upload Architecture Blueprint

## Overview
Structure configured for storing uploaded images/documents using Multer and hosting static files via Express static middleware.

---

## Directory Diagram

```
file-upload-architecture/
├── .env
├── server.js
├── uploads/                    # Stores static uploaded media files
│   └── .gitkeep
├── middleware/
│   └── uploadMiddleware.js     # Multer storage engine & file filter configuration
├── controllers/
│   └── uploadController.js     # Saves file metadata to MySQL database
└── routes/
    └── uploadRoutes.js
```

---

## Static Hosting Code in `server.js`
```javascript
import express from 'express';
import path from 'path';

const app = express();
app.use('/uploads', express.static('uploads'));
```
