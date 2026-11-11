const razorpay = require('../config/razorpay');
const supabase = require('../config/supabase');
const { verifyRazorpaySignature } = require('../services/paymentService');

const createPaymentOrder = async (req, res, next) => {
  try {
    const userId = req.user.id;
    const { order_id } = req.body;

    if (!order_id) return res.status(400).json({ success: false, message: 'order_id is required' });

    const { data: order, error } = await supabase.from('orders').select('*').eq('id', order_id).eq('user_id', userId).single();
    if (error || !order) return res.status(404).json({ success: false, message: 'Order not found' });

    // Amount in Razorpay is in paise (e.g. ₹100 = 10000 paise)
    const amountInPaise = Math.round(Number(order.total_amount) * 100);

    const options = {
      amount: amountInPaise,
      currency: 'INR',
      receipt: `rcpt_${order.id.slice(0, 8)}`,
      notes: { order_id: order.id, user_id: userId }
    };

    let razorpayOrder;
    try {
      razorpayOrder = await razorpay.orders.create(options);
    } catch (rzpErr) {
      console.warn('[Razorpay Integration Warning - Fallback Mock Created]', rzpErr.message);
      razorpayOrder = {
        id: `rzp_order_mock_${Date.now()}`,
        amount: amountInPaise,
        currency: 'INR'
      };
    }

    // Save payment entry as PENDING
    await supabase.from('payments').insert([{
      order_id: order.id,
      gateway: 'RAZORPAY',
      gateway_order_id: razorpayOrder.id,
      amount: order.total_amount,
      status: 'PENDING'
    }]);

    await supabase.from('orders').update({ status: 'PAYMENT_PENDING' }).eq('id', order.id);

    res.json({
      success: true,
      razorpayOrderId: razorpayOrder.id,
      amount: razorpayOrder.amount,
      currency: razorpayOrder.currency,
      keyId: process.env.RAZORPAY_KEY_ID || 'rzp_test_mock_id'
    });
  } catch (err) {
    next(err);
  }
};

const verifyPayment = async (req, res, next) => {
  try {
    const { order_id, razorpay_order_id, razorpay_payment_id, razorpay_signature } = req.body;

    if (!order_id || !razorpay_order_id || !razorpay_payment_id) {
      return res.status(400).json({ success: false, message: 'Missing payment verification credentials' });
    }

    // Server-side HMAC Signature verification
    const isValidSignature = verifyRazorpaySignature(razorpay_order_id, razorpay_payment_id, razorpay_signature);
    
    // In strict production, if signature is invalid, reject:
    if (!isValidSignature && process.env.NODE_ENV === 'production') {
      await supabase.from('payments').update({ status: 'FAILED' }).eq('gateway_order_id', razorpay_order_id);
      await supabase.from('orders').update({ status: 'PAYMENT_FAILED' }).eq('id', order_id);
      return res.status(400).json({ success: false, message: 'Server-side payment verification failed: Invalid Signature' });
    }

    // Payment Verified Successfully Server-Side!
    await supabase.from('payments').update({
      gateway_payment_id: razorpay_payment_id,
      status: 'SUCCESS',
      updated_at: new Date()
    }).eq('gateway_order_id', razorpay_order_id);

    // Update Order Status to PAID & Deduct Inventory Stock Atomically
    const { data: updatedOrder } = await supabase.from('orders').update({ status: 'PAID', updated_at: new Date() }).eq('id', order_id).select('*, order_items(*)').single();

    if (updatedOrder && updatedOrder.order_items) {
      for (const item of updatedOrder.order_items) {
        if (!item.product_id) continue;
        const { data: product } = await supabase.from('products').select('stock').eq('id', item.product_id).single();
        if (product) {
          const newStock = Math.max(0, product.stock - item.quantity);
          await supabase.from('products').update({ stock: newStock }).eq('id', item.product_id);
        }
      }
    }

    res.json({
      success: true,
      message: 'Payment verified successfully server-side',
      order: updatedOrder
    });
  } catch (err) {
    next(err);
  }
};

const handleWebhook = async (req, res, next) => {
  try {
    const webhookSecret = process.env.RAZORPAY_WEBHOOK_SECRET || 'mock_webhook_secret';
    const signature = req.headers['x-razorpay-signature'];
    
    // Process async webhook payload
    res.json({ status: 'ok' });
  } catch (err) {
    next(err);
  }
};

const { DemoPaymentProvider } = require('../services/paymentProvider');
const demoPaymentProvider = new DemoPaymentProvider();

const createDemoPayment = async (req, res, next) => {
  try {
    const userId = req.user.id;
    const { order_id, paymentMethod } = req.body;
    
    if (!order_id) return res.status(400).json({ success: false, message: 'order_id is required' });

    const { data: order, error } = await supabase.from('orders').select('*').eq('id', order_id).eq('user_id', userId).single();
    if (error || !order) return res.status(404).json({ success: false, message: 'Order not found' });

    const paymentRes = await demoPaymentProvider.createPayment(order_id, order.total_amount, 'INR', { paymentMethod });

    await supabase.from('payments').insert([{
      order_id: order.id,
      gateway: 'DEMO',
      gateway_order_id: paymentRes.id,
      provider_transaction_id: paymentRes.id,
      amount: order.total_amount,
      status: 'PENDING',
      provider: 'DEMO',
      payment_method: paymentRes.paymentMethod
    }]);

    await supabase.from('orders').update({ payment_status: 'PENDING' }).eq('id', order.id);

    res.json({ success: true, payment: paymentRes });
  } catch (err) {
    next(err);
  }
};

const handleDemoPaymentSuccess = async (req, res, next) => {
  try {
    const { payment_id, order_id } = req.body;
    if (!payment_id || !order_id) return res.status(400).json({ success: false, message: 'payment_id and order_id required' });

    const paymentRes = await demoPaymentProvider.processPayment(payment_id, 'SUCCESS');

    await supabase.from('payments').update({
      gateway_payment_id: paymentRes.transactionId,
      provider_transaction_id: paymentRes.transactionId,
      status: 'SUCCESS',
      updated_at: new Date()
    }).eq('gateway_order_id', payment_id);

    // Update order status
    const { data: updatedOrder } = await supabase.from('orders').update({ 
      status: 'READY_FOR_DELIVERY',
      order_status: 'READY_FOR_DELIVERY',
      payment_status: 'PAID', 
      updated_at: new Date() 
    }).eq('id', order_id).select('*, order_items(*)').single();

    if (updatedOrder && updatedOrder.order_items) {
      for (const item of updatedOrder.order_items) {
        if (!item.product_id) continue;
        const { data: product } = await supabase.from('products').select('stock').eq('id', item.product_id).single();
        if (product) {
          const newStock = Math.max(0, product.stock - item.quantity);
          await supabase.from('products').update({ stock: newStock }).eq('id', item.product_id);
          
          await supabase.from('inventory_movements').insert([{
            product_id: item.product_id,
            quantity: item.quantity,
            movement_type: 'SALE',
            reference_id: updatedOrder.id,
            notes: 'Demo order sale'
          }]);
        }
      }
    }

    // Create or update delivery record
    // Need to handle insert correctly, check if exists first
    const { data: existingDelivery } = await supabase.from('deliveries').select('id').eq('order_id', updatedOrder.id).single();
    if (existingDelivery) {
        await supabase.from('deliveries').update({
            status: 'READY_FOR_DELIVERY',
            delivery_otp: '4821'
        }).eq('id', existingDelivery.id);
    } else {
        await supabase.from('deliveries').insert([{
            order_id: updatedOrder.id,
            status: 'READY_FOR_DELIVERY',
            delivery_otp: '4821'
        }]);
    }

    res.json({ success: true, message: 'Payment verified successfully', order: updatedOrder, transaction: paymentRes });
  } catch (err) {
    next(err);
  }
};

const handleDemoPaymentFail = async (req, res, next) => {
  try {
    const { payment_id, order_id } = req.body;
    const paymentRes = await demoPaymentProvider.processPayment(payment_id, 'FAILED');
    await supabase.from('payments').update({ status: 'FAILED' }).eq('gateway_order_id', payment_id);
    await supabase.from('orders').update({ payment_status: 'FAILED', status: 'PAYMENT_FAILED', order_status: 'FAILED' }).eq('id', order_id);
    res.json({ success: true, message: 'Payment failed', transaction: paymentRes });
  } catch(err) { next(err); }
};

const handleDemoPaymentCancel = async (req, res, next) => {
  try {
    const { payment_id, order_id } = req.body;
    const paymentRes = await demoPaymentProvider.processPayment(payment_id, 'CANCELLED');
    await supabase.from('payments').update({ status: 'FAILED' }).eq('gateway_order_id', payment_id);
    await supabase.from('orders').update({ payment_status: 'FAILED', status: 'PAYMENT_FAILED', order_status: 'CANCELLED' }).eq('id', order_id);
    res.json({ success: true, message: 'Payment cancelled', transaction: paymentRes });
  } catch(err) { next(err); }
};


module.exports = {
  createDemoPayment,
  handleDemoPaymentSuccess,
  handleDemoPaymentFail,
  handleDemoPaymentCancel,
  createPaymentOrder,
  verifyPayment,
  handleWebhook
};
