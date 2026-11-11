export const errorHandler = (err, req, res, next) => {
  console.error('🔥 Error Handler:', err.message);
  let statusCode = res.statusCode === 200 ? 500 : res.statusCode;
  if (err.code === 'ER_DUP_ENTRY') {
    return res.status(400).json({ success: false, message: 'Course code already exists' });
  }
  if (err.code === 'ER_NO_REFERENCED_ROW_2') {
    return res.status(400).json({ success: false, message: 'Invalid department_id foreign key' });
  }
  res.status(statusCode).json({ success: false, message: err.message || 'Server error' });
};
