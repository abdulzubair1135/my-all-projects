/**
 * Image Specific Upload Module with Strict Validation (MIME type & Size)
 * ES Module Format
 */

import multer from 'multer';
import path from 'path';

// Define Storage Engine
const storage = multer.diskStorage({
  destination: (req, file, cb) => {
    cb(null, 'uploads/images/');
  },
  filename: (req, file, cb) => {
    const uniqueSuffix = Date.now() + '-' + Math.round(Math.random() * 1e9);
    cb(null, `img-${uniqueSuffix}${path.extname(file.originalname)}`);
  }
});

// File Filter Function for Images
const imageFileFilter = (req, file, cb) => {
  const allowedMimeTypes = ['image/jpeg', 'image/png', 'image/jpg', 'image/webp'];

  if (allowedMimeTypes.includes(file.mimetype)) {
    cb(null, true); // Accept file
  } else {
    cb(new Error('Invalid file type! Only JPEG, PNG, and WEBP image files are allowed.'), false); // Reject file
  }
};

// Configured Multer Instance for Images (Max 2MB limit)
export const uploadImage = multer({
  storage: storage,
  fileFilter: imageFileFilter,
  limits: {
    fileSize: 2 * 1024 * 1024 // 2 Megabytes
  }
});

/**
 * Controller Handler
 */
export const handleImageUpload = (req, res) => {
  if (!req.file) {
    return res.status(400).json({
      success: false,
      message: 'Please select an image file to upload',
      error: 'IMAGE_MISSING'
    });
  }

  res.status(200).json({
    success: true,
    message: 'Profile image uploaded successfully',
    data: {
      filename: req.file.filename,
      size: `${(req.file.size / 1024).toFixed(2)} KB`,
      mimeType: req.file.mimetype,
      url: `/uploads/images/${req.file.filename}`
    }
  });
};
