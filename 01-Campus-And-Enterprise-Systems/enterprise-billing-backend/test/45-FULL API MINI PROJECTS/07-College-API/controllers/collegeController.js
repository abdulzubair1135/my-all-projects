import * as CollegeModel from '../models/collegeModel.js';

export const getCourses = async (req, res, next) => {
  try {
    const courses = await CollegeModel.getCoursesWithDepartment();
    res.json({ success: true, message: 'Courses with department details fetched', data: courses });
  } catch (err) { next(err); }
};

export const getCourse = async (req, res, next) => {
  try {
    const course = await CollegeModel.getCourseById(req.params.id);
    if (!course) return res.status(404).json({ success: false, message: 'Course not found' });
    res.json({ success: true, message: 'Course details fetched', data: course });
  } catch (err) { next(err); }
};

export const createCourse = async (req, res, next) => {
  try {
    const id = await CollegeModel.createCourse(req.body);
    res.status(201).json({ success: true, message: 'Course created', data: { id, ...req.body } });
  } catch (err) { next(err); }
};

export const getDepartments = async (req, res, next) => {
  try {
    const depts = await CollegeModel.getAllDepartments();
    res.json({ success: true, message: 'Departments fetched', data: depts });
  } catch (err) { next(err); }
};
