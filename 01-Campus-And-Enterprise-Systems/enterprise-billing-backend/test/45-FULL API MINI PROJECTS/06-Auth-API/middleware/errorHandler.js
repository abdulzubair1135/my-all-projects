export const errorHandler = (err, req, res, next) => {
  console.error('🔥 Error Handler:', err.message);
  res.status(500).json({ success: false, message: err.message || 'Server error' });
};
