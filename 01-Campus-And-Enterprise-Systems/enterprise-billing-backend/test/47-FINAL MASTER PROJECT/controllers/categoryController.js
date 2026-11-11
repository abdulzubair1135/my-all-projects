import * as CategoryModel from '../models/categoryModel.js';
import { sendSuccess, sendError } from '../utils/response.js';

export const getCategories = async (req, res, next) => {
  try {
    const categories = await CategoryModel.getAllCategories();
    return sendSuccess(res, 'Categories retrieved successfully', categories);
  } catch (error) {
    next(error);
  }
};

export const getCategory = async (req, res, next) => {
  try {
    const category = await CategoryModel.getCategoryById(req.params.id);
    if (!category) return sendError(res, 'Category not found', null, 404);
    return sendSuccess(res, 'Category details retrieved', category);
  } catch (error) {
    next(error);
  }
};

export const createCategory = async (req, res, next) => {
  try {
    const { category_name, description } = req.body;
    const id = await CategoryModel.createCategory(category_name, description);
    return sendSuccess(res, 'Category created', { id, category_name, description }, 201);
  } catch (error) {
    next(error);
  }
};

export const updateCategory = async (req, res, next) => {
  try {
    const { category_name, description } = req.body;
    const affected = await CategoryModel.updateCategory(req.params.id, category_name, description);
    if (!affected) return sendError(res, 'Category not found', null, 404);
    return sendSuccess(res, 'Category updated', { id: req.params.id, category_name, description });
  } catch (error) {
    next(error);
  }
};

export const deleteCategory = async (req, res, next) => {
  try {
    const affected = await CategoryModel.deleteCategory(req.params.id);
    if (!affected) return sendError(res, 'Category not found', null, 404);
    return sendSuccess(res, 'Category deleted successfully');
  } catch (error) {
    next(error);
  }
};
