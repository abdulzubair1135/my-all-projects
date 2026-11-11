import * as OrderModel from '../models/orderModel.js';
import { sendSuccess, sendError } from '../utils/response.js';

export const checkout = async (req, res, next) => {
  try {
    const userId = req.user.id;
    const { shipping_address, items } = req.body;

    const result = await OrderModel.createOrderTransaction(userId, shipping_address, items);
    return sendSuccess(res, 'Order placed successfully using database transaction!', result, 201);
  } catch (error) {
    next(error);
  }
};

export const getMyOrders = async (req, res, next) => {
  try {
    const orders = await OrderModel.getUserOrders(req.user.id);
    return sendSuccess(res, 'User orders retrieved', orders);
  } catch (error) {
    next(error);
  }
};

export const getOrderDetails = async (req, res, next) => {
  try {
    const orderId = req.params.id;
    // Allow admins to view any order, customers can only view their own
    const userId = req.user.role === 'admin' ? null : req.user.id;

    const order = await OrderModel.getOrderByIdDetails(orderId, userId);
    if (!order) {
      return sendError(res, 'Order not found or unauthorized access.', null, 404);
    }
    return sendSuccess(res, 'Order details fetched', order);
  } catch (error) {
    next(error);
  }
};
