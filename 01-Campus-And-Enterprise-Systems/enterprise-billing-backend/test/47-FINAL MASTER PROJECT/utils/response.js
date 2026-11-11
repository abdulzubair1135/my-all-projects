export const sendSuccess = (res, message = 'Success', data = null, statusCode = 200, extra = {}) => {
  return res.status(statusCode).json({
    success: true,
    message,
    ...(data !== null && { data }),
    ...extra
  });
};

export const sendError = (res, message = 'An error occurred', error = null, statusCode = 500) => {
  return res.status(statusCode).json({
    success: false,
    message,
    ...(error !== null && { error })
  });
};
