import express from 'express';
import { getStudents, getStudent, createStudent, updateStudent, deleteStudent } from '../controllers/studentController.js';
import { validateStudent } from '../validation/studentValidation.js';

const router = express.Router();

router.get('/', getStudents);
router.get('/:id', getStudent);
router.post('/', validateStudent, createStudent);
router.put('/:id', validateStudent, updateStudent);
router.delete('/:id', deleteStudent);

export default router;
