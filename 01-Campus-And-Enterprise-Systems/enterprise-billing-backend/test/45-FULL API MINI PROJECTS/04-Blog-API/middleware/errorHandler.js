export const errorHandler = (err, req, res, next) => {
  console.error('🔥 Error Handler:', err.message);
  let statusCode = res.statusCode === 200 ? 500 : res.statusCode;
  if (err.code === 'ER_DUP_ENTRY') {
    return res.status(400).json({ success: false, message: 'Slug already exists' });
  }
  res.status(statusCode).json({ success: false, message: err.message || 'Server error' });
};
