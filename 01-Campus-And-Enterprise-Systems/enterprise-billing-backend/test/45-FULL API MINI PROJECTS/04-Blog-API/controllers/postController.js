import * as PostModel from '../models/postModel.js';

export const getPosts = async (req, res, next) => {
  try {
    const posts = await PostModel.getAll();
    res.json({ success: true, message: 'Posts retrieved', data: posts });
  } catch (err) { next(err); }
};

export const getPost = async (req, res, next) => {
  try {
    const post = await PostModel.getById(req.params.id);
    if (!post) return res.status(404).json({ success: false, message: 'Post not found' });
    res.json({ success: true, message: 'Post retrieved', data: post });
  } catch (err) { next(err); }
};

export const createPost = async (req, res, next) => {
  try {
    const id = await PostModel.create(req.body);
    res.status(201).json({ success: true, message: 'Post created', data: { id, ...req.body } });
  } catch (err) { next(err); }
};

export const updatePost = async (req, res, next) => {
  try {
    const affected = await PostModel.update(req.params.id, req.body);
    if (!affected) return res.status(404).json({ success: false, message: 'Post not found' });
    res.json({ success: true, message: 'Post updated', data: { id: req.params.id, ...req.body } });
  } catch (err) { next(err); }
};

export const deletePost = async (req, res, next) => {
  try {
    const affected = await PostModel.remove(req.params.id);
    if (!affected) return res.status(404).json({ success: false, message: 'Post not found' });
    res.json({ success: true, message: 'Post deleted' });
  } catch (err) { next(err); }
};
