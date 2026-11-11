/**
 * Multiple File Upload Controller & Middleware
 * ES Module Format
 */

import uploadBasic from './multer-basic.js';

/**
 * 1. Upload multiple files from a single input field 'documents' (Max 5 files)
 */
export const uploadMultipleDocuments = uploadBasic.array('documents', 5);

/**
 * 2. Upload multiple files from multiple fields ('avatar' and 'certificates')
 */
export const uploadMultipleFields = uploadBasic.fields([
  { name: 'avatar', maxCount: 1 },
  { name: 'certificates', maxCount: 3 }
]);

/**
 * Controller to Handle Multiple Files Array Response
 */
export const handleMultipleUploads = (req, res) => {
  if (!req.files || req.files.length === 0) {
    return res.status(400).json({
      success: false,
      message: 'No files were uploaded',
      error: 'FILES_MISSING'
    });
  }

  const uploadedFiles = req.files.map(file => ({
    originalName: file.originalname,
    filename: file.filename,
    size: file.size,
    url: `/uploads/${file.filename}`
  }));

  res.status(200).json({
    success: true,
    message: `${uploadedFiles.length} files uploaded successfully`,
    data: uploadedFiles
  });
};
