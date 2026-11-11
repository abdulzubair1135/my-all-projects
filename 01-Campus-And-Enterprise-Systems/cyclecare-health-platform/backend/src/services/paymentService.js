const crypto = require('crypto');

function verifyRazorpaySignature(orderId, paymentId, signature, secretKey) {
  if (!orderId || !paymentId || !signature) return false;
  const key = secretKey || process.env.RAZORPAY_KEY_SECRET || 'mock_secret_key';
  
  const hmac = crypto.createHmac('sha256', key);
  hmac.update(`${orderId}|${paymentId}`);
  const generatedSignature = hmac.digest('hex');
  
  return generatedSignature === signature;
}

module.exports = {
  verifyRazorpaySignature
};
