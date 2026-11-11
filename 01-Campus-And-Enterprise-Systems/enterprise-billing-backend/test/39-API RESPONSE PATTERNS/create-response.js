/**
 * Standard Resource Creation Response Utility Helper
 * ES Module Format
 */

/**
 * Sends HTTP 201 Created response for newly created database resources
 * @param {Object} res - Express response object
 * @param {Object} createdResource - Details of the newly created entity
 * @param {string} message - Success message
 */
export const sendCreated = (
  res,
  createdResource,
  message = 'Resource created successfully'
) => {
  return res.status(201).json({
    success: true,
    message: message,
    data: createdResource
  });
};

export default sendCreated;
