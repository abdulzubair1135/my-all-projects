import * as ProductModel from '../models/productModel.js';
import { sendSuccess, sendError } from '../utils/response.js';

export const getProducts = async (req, res, next) => {
  try {
    const search = req.query.search || '';
    const category_id = req.query.category_id || null;
    const page = parseInt(req.query.page) || 1;
    const limit = parseInt(req.query.limit) || 10;

    const result = await ProductModel.getProductsPaginated({ search, category_id, page, limit });
    return sendSuccess(res, 'Products fetched successfully', result.products, 200, {
      pagination: {
        total: result.total,
        totalPages: result.totalPages,
        currentPage: result.currentPage,
        limit: result.limit
      }
    });
  } catch (error) {
    next(error);
  }
};

export const getProduct = async (req, res, next) => {
  try {
    const product = await ProductModel.getProductById(req.params.id);
    if (!product) return sendError(res, 'Product not found', null, 404);
    return sendSuccess(res, 'Product details fetched', product);
  } catch (error) {
    next(error);
  }
};

export const createProduct = async (req, res, next) => {
  try {
    let image_url = null;
    if (req.file) {
      image_url = `/uploads/${req.file.filename}`;
    }
    const productData = { ...req.body, image_url };
    const id = await ProductModel.createProduct(productData);
    return sendSuccess(res, 'Product created successfully', { id, ...productData }, 201);
  } catch (error) {
    next(error);
  }
};

export const updateProduct = async (req, res, next) => {
  try {
    let image_url = null;
    if (req.file) {
      image_url = `/uploads/${req.file.filename}`;
    }
    const productData = { ...req.body, image_url };
    const affected = await ProductModel.updateProduct(req.params.id, productData);
    if (!affected) return sendError(res, 'Product not found', null, 404);
    return sendSuccess(res, 'Product updated successfully', { id: req.params.id, ...productData });
  } catch (error) {
    next(error);
  }
};

export const deleteProduct = async (req, res, next) => {
  try {
    const affected = await ProductModel.deleteProduct(req.params.id);
    if (!affected) return sendError(res, 'Product not found', null, 404);
    return sendSuccess(res, 'Product deleted successfully');
  } catch (error) {
    next(error);
  }
};
