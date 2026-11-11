import express from 'express';
import { getEmployees, getEmployee, createEmployee, updateEmployee, deleteEmployee } from '../controllers/employeeController.js';
import { validateEmployee } from '../validation/employeeValidation.js';

const router = express.Router();
router.get('/', getEmployees);
router.get('/:id', getEmployee);
router.post('/', validateEmployee, createEmployee);
router.put('/:id', validateEmployee, updateEmployee);
router.delete('/:id', deleteEmployee);

export default router;
