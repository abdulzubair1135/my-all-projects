/**
 * Multer Basic Configuration Module
 * ES Module Format
 */

import multer from 'multer';
import path from 'path';
import fs from 'fs';

// Ensure uploads directory exists on server startup
const uploadDir = 'uploads/';
if (!fs.existsSync(uploadDir)) {
  fs.mkdirSync(uploadDir, { recursive: true });
}

/**
 * Define Disk Storage Engine
 */
const storage = multer.diskStorage({
  // Destination directory for saved files
  destination: (req, file, cb) => {
    cb(null, uploadDir);
  },
  
  // Custom unique filename generator (timestamp-random.ext)
  filename: (req, file, cb) => {
    const uniqueSuffix = Date.now() + '-' + Math.round(Math.random() * 1e9);
    const fileExt = path.extname(file.originalname);
    cb(null, `${file.fieldname}-${uniqueSuffix}${fileExt}`);
  }
});

/**
 * Export Basic Multer Middleware Instance
 */
export const uploadBasic = multer({ storage: storage });

export default uploadBasic;
