import * as StudentModel from '../models/studentModel.js';

export const getStudents = async (req, res, next) => {
  try {
    const students = await StudentModel.getAllStudents();
    res.status(200).json({
      success: true,
      message: 'Students fetched successfully',
      data: students
    });
  } catch (error) {
    next(error);
  }
};

export const getStudent = async (req, res, next) => {
  try {
    const student = await StudentModel.getStudentById(req.params.id);
    if (!student) {
      return res.status(404).json({
        success: false,
        message: 'Student not found',
        error: 'ID does not exist'
      });
    }
    res.status(200).json({
      success: true,
      message: 'Student details fetched',
      data: student
    });
  } catch (error) {
    next(error);
  }
};

export const createStudent = async (req, res, next) => {
  try {
    const newId = await StudentModel.createStudent(req.body);
    res.status(201).json({
      success: true,
      message: 'Student created successfully',
      data: { id: newId, ...req.body }
    });
  } catch (error) {
    next(error);
  }
};

export const updateStudent = async (req, res, next) => {
  try {
    const affected = await StudentModel.updateStudent(req.params.id, req.body);
    if (affected === 0) {
      return res.status(404).json({
        success: false,
        message: 'Student not found',
        error: 'Update failed'
      });
    }
    res.status(200).json({
      success: true,
      message: 'Student updated successfully',
      data: { id: req.params.id, ...req.body }
    });
  } catch (error) {
    next(error);
  }
};

export const deleteStudent = async (req, res, next) => {
  try {
    const affected = await StudentModel.deleteStudent(req.params.id);
    if (affected === 0) {
      return res.status(404).json({
        success: false,
        message: 'Student not found',
        error: 'Delete failed'
      });
    }
    res.status(200).json({
      success: true,
      message: 'Student deleted successfully'
    });
  } catch (error) {
    next(error);
  }
};
