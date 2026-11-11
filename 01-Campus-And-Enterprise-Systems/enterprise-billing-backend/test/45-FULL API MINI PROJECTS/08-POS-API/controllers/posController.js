import * as POSModel from '../models/posModel.js';

export const checkoutOrder = async (req, res, next) => {
  try {
    const { customer_name, items } = req.body;
    const result = await POSModel.createOrderWithTransaction(customer_name, items);
    res.status(201).json({
      success: true,
      message: 'Order checked out successfully using DB transaction',
      data: result
    });
  } catch (err) {
    next(err);
  }
};

export const getOrders = async (req, res, next) => {
  try {
    const orders = await POSModel.getAllOrders();
    res.json({ success: true, message: 'Orders list retrieved', data: orders });
  } catch (err) {
    next(err);
  }
};

export const getOrder = async (req, res, next) => {
  try {
    const order = await POSModel.getOrderDetails(req.params.id);
    if (!order) return res.status(404).json({ success: false, message: 'Order not found' });
    res.json({ success: true, message: 'Order details retrieved', data: order });
  } catch (err) {
    next(err);
  }
};
