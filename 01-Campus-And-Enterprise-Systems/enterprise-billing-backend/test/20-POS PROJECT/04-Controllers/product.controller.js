/**
 * Product Controller
 */

import { validationResult } from 'express-validator';
import Product from '../03-Models/Product.js';
import Franchise from '../03-Models/Franchise.js';

export const getProducts = async (req, res, next) => {
  try {
    const { franchise_id } = req.query;
    const products = await Product.findAll(franchise_id);

    return res.status(200).json({
      success: true,
      message: 'Products list fetched successfully',
      data: products
    });
  } catch (error) {
    next(error);
  }
};

export const getProductById = async (req, res, next) => {
  try {
    const { id } = req.params;
    const product = await Product.findById(id);

    if (!product) {
      return res.status(404).json({ success: false, message: 'Product not found', error: 'NOT_FOUND' });
    }

    return res.status(200).json({
      success: true,
      message: 'Product details fetched successfully',
      data: product
    });
  } catch (error) {
    next(error);
  }
};

export const createProduct = async (req, res, next) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ success: false, message: 'Validation failed', error: errors.array() });
    }

    const { franchise_id, name, category, price, stock } = req.body;

    const franchise = await Franchise.findById(franchise_id);
    if (!franchise) {
      return res.status(404).json({ success: false, message: 'Franchise does not exist', error: 'INVALID_FRANCHISE' });
    }

    const newProduct = await Product.create({ franchise_id, name, category, price, stock });
    return res.status(201).json({
      success: true,
      message: 'Product created successfully',
      data: newProduct
    });
  } catch (error) {
    next(error);
  }
};
