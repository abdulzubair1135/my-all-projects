const Razorpay = require('razorpay');
require('dotenv').config();

const key_id = process.env.RAZORPAY_KEY_ID || 'rzp_test_mock_id';
const key_secret = process.env.RAZORPAY_KEY_SECRET || 'mock_secret_key';

const razorpayInstance = new Razorpay({
  key_id: key_id,
  key_secret: key_secret
});

module.exports = razorpayInstance;
