# File Upload Validation Guide (`file-validation.md`)

When accepting uploaded files in Node.js applications using `multer`, validating file size and file format/type is critical to prevent denial of service (DoS) attacks and malicious file execution.

---

## 1. Key Validation Criteria

1. **File Extension & MIME Type Filtering**: Restrict file uploads to safe formats (e.g. `.png`, `.jpg`, `.pdf`). Never allow executable uploads like `.exe`, `.sh`, or `.php`.
2. **File Size Limits**: Set strict limits (`fileSize`) to prevent server memory saturation.
3. **Number of Files**: Limit maximum file count per request.

---

## 2. Setting Size Limits in Multer

Multer exposes a `limits` configuration object:

```javascript
import multer from 'multer';

const upload = multer({
  dest: 'uploads/',
  limits: {
    fileSize: 5 * 1024 * 1024, // 5MB limit in bytes
    files: 3                  // Max 3 files per upload request
  }
});
```

---

## 3. Implementing Custom `fileFilter`

```javascript
const customFileFilter = (req, file, cb) => {
  // Check MIME type
  const allowedMimeTypes = ['application/pdf', 'image/jpeg', 'image/png'];
  
  if (allowedMimeTypes.includes(file.mimetype)) {
    cb(null, true); // Accept file
  } else {
    // Return error message
    cb(new Error('INVALID_FILE_TYPE: Only PDF, JPG, and PNG files are allowed!'), false);
  }
};
```

---

## 4. Handling Multer Validation Errors in Express

Multer errors occur during middleware execution. Catch them in a custom wrapper or route error handler:

```javascript
import multer from 'multer';

export const handleMulterUpload = (uploadMiddleware) => {
  return (req, res, next) => {
    uploadMiddleware(req, res, (err) => {
      if (err instanceof multer.MulterError) {
        // Multer specific error (e.g., file size limit exceeded)
        if (err.code === 'LIMIT_FILE_SIZE') {
          return res.status(400).json({
            success: false,
            message: 'File size exceeds maximum 2MB limit',
            error: err.code
          });
        }
        return res.status(400).json({
          success: false,
          message: err.message,
          error: err.code
        });
      } else if (err) {
        // Custom error thrown by fileFilter
        return res.status(400).json({
          success: false,
          message: err.message,
          error: 'FILE_VALIDATION_ERROR'
        });
      }
      // If no error, proceed to controller
      next();
    });
  };
};
```
