import * as ProdModel from '../models/productModel.js';

export const getProducts = async (req, res, next) => {
  try {
    const products = await ProdModel.getAll();
    res.json({ success: true, message: 'Products fetched', data: products });
  } catch (err) { next(err); }
};

export const getProduct = async (req, res, next) => {
  try {
    const product = await ProdModel.getById(req.params.id);
    if (!product) return res.status(404).json({ success: false, message: 'Product not found' });
    res.json({ success: true, message: 'Product details fetched', data: product });
  } catch (err) { next(err); }
};

export const createProduct = async (req, res, next) => {
  try {
    const id = await ProdModel.create(req.body);
    res.status(201).json({ success: true, message: 'Product created', data: { id, ...req.body } });
  } catch (err) { next(err); }
};

export const updateProduct = async (req, res, next) => {
  try {
    const affected = await ProdModel.update(req.params.id, req.body);
    if (!affected) return res.status(404).json({ success: false, message: 'Product not found' });
    res.json({ success: true, message: 'Product updated', data: { id: req.params.id, ...req.body } });
  } catch (err) { next(err); }
};

export const deleteProduct = async (req, res, next) => {
  try {
    const affected = await ProdModel.remove(req.params.id);
    if (!affected) return res.status(404).json({ success: false, message: 'Product not found' });
    res.json({ success: true, message: 'Product deleted' });
  } catch (err) { next(err); }
};
