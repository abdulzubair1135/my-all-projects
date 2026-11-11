/**
 * Complete Express Upload Routes Module
 * ES Module Format
 */

import express from 'express';
import { uploadSingleAvatar, handleSingleUpload } from './single-upload.js';
import { uploadMultipleDocuments, handleMultipleUploads } from './multiple-upload.js';
import { uploadImage, handleImageUpload } from './image-upload.js';
import { handleMulterUpload } from './file-validation.js';

const router = express.Router();

/**
 * Route 1: Single Profile Avatar Upload
 * POST /api/upload/avatar
 */
router.post('/avatar', uploadSingleAvatar, handleSingleUpload);

/**
 * Route 2: Multiple Document Upload (Max 5 files)
 * POST /api/upload/documents
 */
router.post('/documents', uploadMultipleDocuments, handleMultipleUploads);

/**
 * Route 3: Validated Profile Image Upload (Max 2MB, Image MIME filter)
 * POST /api/upload/image
 */
router.post('/image', handleMulterUpload(uploadImage.single('profilePic')), handleImageUpload);

export default router;
