# SET 06 - File Upload with Multer

## Question
Implement Image Upload middleware using `multer` for Profile Picture updates. Only allow `.jpg`, `.jpeg`, and `.png` files under 2MB.

---

## Requirements
1. Storage location: `./uploads/`.
2. Generate unique filenames using `Date.now() + '-' + file.originalname`.
3. Filter mime types to allow only images.
4. Limit max file size to 2MB (2 * 1024 * 1024 bytes).

---

## Solution Code

### `middleware/uploadMiddleware.js`
```javascript
import multer from 'multer';
import path from 'path';

const storage = multer.diskStorage({
  destination: (req, file, cb) => {
    cb(null, 'uploads/');
  },
  filename: (req, file, cb) => {
    const uniqueSuffix = Date.now() + '-' + Math.round(Math.random() * 1e9);
    cb(null, uniqueSuffix + path.extname(file.originalname));
  }
});

const fileFilter = (req, file, cb) => {
  const allowedTypes = /jpeg|jpg|png|webp/;
  const extname = allowedTypes.test(path.extname(file.originalname).toLowerCase());
  const mimetype = allowedTypes.test(file.mimetype);

  if (extname && mimetype) {
    return cb(null, true);
  } else {
    cb(new Error('Only image files (jpg, jpeg, png, webp) are allowed!'));
  }
};

export const upload = multer({
  storage,
  limits: { fileSize: 2 * 1024 * 1024 }, // 2MB
  fileFilter
});
```

### Route Usage
```javascript
import { upload } from '../middleware/uploadMiddleware.js';

router.post('/avatar', upload.single('avatar'), (req, res) => {
  if (!req.file) return res.status(400).json({ success: false, message: 'Please upload a file' });
  res.json({ success: true, message: 'File uploaded', filePath: `/uploads/${req.file.filename}` });
});
```

---

## Postman Test Guide
- `POST http://localhost:5000/api/users/avatar`
- Body -> `form-data` -> Key: `avatar` (type File) -> Select image -> Send.
