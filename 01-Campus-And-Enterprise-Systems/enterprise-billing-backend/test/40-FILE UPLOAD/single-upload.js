/**
 * Single File Upload Controller & Middleware
 * ES Module Format
 */

import uploadBasic from './multer-basic.js';

/**
 * Express Middleware for Single File Field 'avatar'
 */
export const uploadSingleAvatar = uploadBasic.single('avatar');

/**
 * Controller to Handle Single File Upload Completion
 */
export const handleSingleUpload = (req, res) => {
  // Check if file was provided in request
  if (!req.file) {
    return res.status(400).json({
      success: false,
      message: 'No file uploaded',
      error: 'FILE_MISSING'
    });
  }

  // Information provided by Multer on req.file
  const fileDetails = {
    originalName: req.file.originalname,
    filename: req.file.filename,
    mimeType: req.file.mimetype,
    sizeInBytes: req.file.size,
    path: req.file.path,
    publicUrl: `/uploads/${req.file.filename}`
  };

  res.status(200).json({
    success: true,
    message: 'Single file uploaded successfully',
    data: fileDetails
  });
};

export default { uploadSingleAvatar, handleSingleUpload };
