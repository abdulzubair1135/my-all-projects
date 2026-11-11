/**
 * Nested Routes / Sub-Resource Routing Module (mergeParams: true)
 * ES Module Format
 */

import express from 'express';

// Enable mergeParams to access parent route parameters (e.g. :courseId)
const router = express.Router({ mergeParams: true });

/**
 * Get all students enrolled in a specific course
 * GET /api/courses/:courseId/students
 */
router.get('/', (req, res) => {
  const { courseId } = req.params;
  res.status(200).json({
    success: true,
    message: `Retrieved students enrolled in Course ID ${courseId}`,
    data: [
      { id: 1, name: 'Student A', courseId: courseId },
      { id: 2, name: 'Student B', courseId: courseId }
    ]
  });
});

/**
 * Enroll a student into a specific course
 * POST /api/courses/:courseId/students
 */
router.post('/', (req, res) => {
  const { courseId } = req.params;
  const { studentId } = req.body;

  res.status(201).json({
    success: true,
    message: `Student ${studentId} successfully enrolled into Course ${courseId}`
  });
});

export default router;
