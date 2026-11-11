import express from 'express';
import { getCourses, getCourse, createCourse, getDepartments } from '../controllers/collegeController.js';
import { validateCourse } from '../validation/collegeValidation.js';

const router = express.Router();
router.get('/courses', getCourses);
router.get('/courses/:id', getCourse);
router.post('/courses', validateCourse, createCourse);
router.get('/departments', getDepartments);

export default router;
