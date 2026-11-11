/**
 * Standard Paginated Response Utility Helper
 * ES Module Format
 */

/**
 * Sends a standardized HTTP paginated success response
 * @param {Object} res - Express response object
 * @param {Array} items - List of items for current page
 * @param {number} page - Current page number
 * @param {number} limit - Items per page
 * @param {number} totalRecords - Total count of records in DB matching filter
 * @param {string} message - Success message
 */
export const sendPaginated = (
  res,
  items = [],
  page = 1,
  limit = 10,
  totalRecords = 0,
  message = 'Paginated data retrieved successfully'
) => {
  const currentPage = parseInt(page, 10);
  const perPage = parseInt(limit, 10);
  const total = parseInt(totalRecords, 10);
  const totalPages = Math.ceil(total / perPage) || 1;

  return res.status(200).json({
    success: true,
    message: message,
    data: items,
    pagination: {
      currentPage: currentPage,
      limit: perPage,
      totalRecords: total,
      totalPages: totalPages,
      hasNextPage: currentPage < totalPages,
      hasPrevPage: currentPage > 1
    }
  });
};

export default sendPaginated;
