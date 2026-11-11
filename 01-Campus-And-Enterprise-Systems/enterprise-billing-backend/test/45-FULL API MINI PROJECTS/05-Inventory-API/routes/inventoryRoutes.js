import express from 'express';
import { getItems, getItem, createItem, updateItem, deleteItem } from '../controllers/inventoryController.js';
import { validateInventory } from '../validation/inventoryValidation.js';

const router = express.Router();
router.get('/', getItems);
router.get('/:id', getItem);
router.post('/', validateInventory, createItem);
router.put('/:id', validateInventory, updateItem);
router.delete('/:id', deleteItem);

export default router;
