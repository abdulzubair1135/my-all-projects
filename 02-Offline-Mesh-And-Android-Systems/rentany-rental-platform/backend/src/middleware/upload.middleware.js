import { v2 as cloudinary } from 'cloudinary';
import multer from 'multer';
import path from 'path';
import { env } from '../config/env.js';
import { AppError } from './error.middleware.js';

// Configure Cloudinary SDK
cloudinary.config({
  cloud_name: env.CLOUDINARY_CLOUD_NAME,
  api_key: env.CLOUDINARY_API_KEY,
  api_secret: env.CLOUDINARY_API_SECRET
});

// Multer memory storage configuration (ephemeral buffer for serverless compatibility)
const storage = multer.memoryStorage();

// File filter to restrict uploads to images only
const fileFilter = (req, file, cb) => {
  const allowedExtensions = ['.jpg', '.jpeg', '.png', '.webp', '.gif'];
  const allowedMimeTypes = ['image/jpeg', 'image/png', 'image/webp', 'image/gif'];
  
  const ext = path.extname(file.originalname).toLowerCase();
  const mime = file.mimetype;

  if (allowedExtensions.includes(ext) && allowedMimeTypes.includes(mime)) {
    cb(null, true);
  } else {
    cb(new AppError('Only image files (JPG, JPEG, PNG, WEBP, GIF) are allowed.', 400), false);
  }
};

// Multer upload middleware
export const upload = multer({
  storage: storage,
  limits: {
    fileSize: env.UPLOAD_MAX_SIZE
  },
  fileFilter: fileFilter
});

/**
 * Uploads a file buffer directly to Cloudinary using streaming upload
 * @param {Buffer} fileBuffer The file content buffer
 * @returns {Promise<object>} Cloudinary upload result containing secure_url
 */
export const uploadToCloudinary = (fileBuffer) => {
  return new Promise((resolve, reject) => {
    // If Cloudinary keys are missing (e.g. local test mode), resolve with a placeholder image URL
    if (!env.CLOUDINARY_CLOUD_NAME || !env.CLOUDINARY_API_KEY || !env.CLOUDINARY_API_SECRET) {
      console.log('[Warning] Cloudinary credentials missing. Mocking upload secure_url.');
      return resolve({
        secure_url: 'https://images.unsplash.com/photo-1516035069371-29a1b244cc32?auto=format&fit=crop&q=80&w=500',
        public_id: 'mock_cloudinary_public_id'
      });
    }

    const stream = cloudinary.uploader.upload_stream(
      {
        folder: 'rentany',
        resource_type: 'image'
      },
      (error, result) => {
        if (error) {
          console.error('Cloudinary stream upload error:', error);
          reject(new AppError('Image upload failed at media cloud service.', 502));
        } else {
          resolve(result);
        }
      }
    );
    stream.end(fileBuffer);
  });
};
