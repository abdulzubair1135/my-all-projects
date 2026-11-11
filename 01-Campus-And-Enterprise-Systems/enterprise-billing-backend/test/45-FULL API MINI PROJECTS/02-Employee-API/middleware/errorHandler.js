export const errorHandler = (err, req, res, next) => {
  console.error('🔥 Error Handler:', err.message);
  let statusCode = res.statusCode === 200 ? 500 : res.statusCode;
  if (err.code === 'ER_DUP_ENTRY') {
    statusCode = 400;
    return res.status(400).json({ success: false, message: 'Employee code or email already exists' });
  }
  res.status(statusCode).json({ success: false, message: err.message || 'Server error' });
};
