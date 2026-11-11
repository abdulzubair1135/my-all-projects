/**
 * User Routes Definition
 */

import express from 'express';
import {
  getAllUsers,
  getUserById,
  createUser,
  updateUser,
  deleteUser
} from '../controllers/user.controller.js';
import {
  userValidationRules,
  idValidationRule
} from '../validation/user.validation.js';

const router = express.Router();

// Base Path: /api/users

// GET All Users
router.get('/', getAllUsers);

// GET User by ID
router.get('/:id', idValidationRule, getUserById);

// POST Create User
router.post('/', userValidationRules, createUser);

// PUT Update User
router.put('/:id', [...idValidationRule, ...userValidationRules], updateUser);

// DELETE User
router.delete('/:id', idValidationRule, deleteUser);

export default router;
