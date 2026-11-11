/**
 * Bill / Invoice Controller for POS Application
 * Cart totals calculation, stock updates & invoice generation.
 */

import { validationResult } from 'express-validator';
import Bill from '../03-Models/Bill.js';
import Product from '../03-Models/Product.js';

export const getBills = async (req, res, next) => {
  try {
    const bills = await Bill.findAll();
    return res.status(200).json({
      success: true,
      message: 'Bills list fetched successfully',
      data: bills
    });
  } catch (error) {
    next(error);
  }
};

export const getBillById = async (req, res, next) => {
  try {
    const { id } = req.params;
    const bill = await Bill.findById(id);

    if (!bill) {
      return res.status(404).json({ success: false, message: 'Bill invoice not found', error: 'NOT_FOUND' });
    }

    return res.status(200).json({
      success: true,
      message: 'Bill details fetched successfully',
      data: bill
    });
  } catch (error) {
    next(error);
  }
};

export const generateBill = async (req, res, next) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ success: false, message: 'Validation failed', error: errors.array() });
    }

    const { franchise_id, customer_name, items, tax_rate = 0.18 } = req.body;
    const user_id = req.user.id; // Logged in Cashier ID

    let subtotal = 0;
    const processedItems = [];

    // Verify products availability & calculate subtotal
    for (const item of items) {
      const product = await Product.findById(item.product_id);
      if (!product) {
        return res.status(400).json({
          success: false,
          message: `Product ID ${item.product_id} not found`,
          error: 'PRODUCT_NOT_FOUND'
        });
      }

      if (product.stock < item.quantity) {
        return res.status(400).json({
          success: false,
          message: `Insufficient stock for product: ${product.name}. Available: ${product.stock}`,
          error: 'INSUFFICIENT_STOCK'
        });
      }

      const itemTotal = Number(product.price) * item.quantity;
      subtotal += itemTotal;

      processedItems.push({
        product_id: product.id,
        name: product.name,
        price: Number(product.price),
        quantity: item.quantity,
        total: itemTotal
      });
    }

    const tax_amount = Number((subtotal * Number(tax_rate)).toFixed(2));
    const grand_total = Number((subtotal + tax_amount).toFixed(2));

    // Unique Bill Number Generation
    const bill_number = `INV-${Date.now()}-${Math.floor(100 + Math.random() * 900)}`;

    // Create Invoice in DB
    const newBill = await Bill.create({
      bill_number,
      franchise_id,
      user_id,
      customer_name,
      subtotal,
      tax_rate,
      tax_amount,
      grand_total,
      items: processedItems
    });

    // Deduct stock for sold items
    for (const item of items) {
      const product = await Product.findById(item.product_id);
      await Product.updateStock(product.id, product.stock - item.quantity);
    }

    return res.status(201).json({
      success: true,
      message: 'Invoice generated successfully',
      data: newBill
    });
  } catch (error) {
    next(error);
  }
};
