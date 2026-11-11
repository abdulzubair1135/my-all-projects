/**
 * Combined Pagination, Search, Sorting, and Filtering Route & Controller
 * ES Module Format
 */

import express from 'express';
import { query, validationResult } from 'express-validator';
import { sendPaginated } from '../39-API RESPONSE PATTERNS/pagination-response.js';

const router = express.Router();

// Allowed Columns Whitelist for Sorting
const ALLOWED_SORT_COLUMNS = ['id', 'name', 'course', 'marks', 'created_at'];

/**
 * Validation Middleware Chain for Query Parameters
 */
export const validateQueryOptions = [
  query('page').optional().isInt({ min: 1 }).toInt(),
  query('limit').optional().isInt({ min: 1, max: 100 }).toInt(),
  query('search').optional().trim().escape(),
  query('course').optional().trim(),
  query('sortBy').optional().isIn(ALLOWED_SORT_COLUMNS),
  query('sortOrder').optional().toUpperCase().isIn(['ASC', 'DESC']),
  (req, res, next) => {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ success: false, errors: errors.array() });
    }
    next();
  }
];

/**
 * Master Controller Combining Search, Filter, Sort, and Paginate
 */
export const searchAndPaginateStudents = async (req, res, next) => {
  try {
    const page = req.query.page || 1;
    const limit = req.query.limit || 10;
    const offset = (page - 1) * limit;
    const search = req.query.search || '';
    const course = req.query.course || '';
    const sortBy = ALLOWED_SORT_COLUMNS.includes(req.query.sortBy) ? req.query.sortBy : 'id';
    const sortOrder = req.query.sortOrder === 'DESC' ? 'DESC' : 'ASC';

    // 1. Dynamic SQL Building Pattern
    let whereClause = 'WHERE 1=1';
    const queryParams = [];

    if (search) {
      whereClause += ' AND (name LIKE ? OR email LIKE ?)';
      queryParams.push(`%${search}%`, `%${search}%`);
    }

    if (course) {
      whereClause += ' AND course = ?';
      queryParams.push(course);
    }

    /* SQL Execution logic:
    const countSql = `SELECT COUNT(*) as total FROM students ${whereClause}`;
    const [[{ total }]] = await pool.query(countSql, queryParams);

    const dataSql = `SELECT id, name, email, course, marks FROM students ${whereClause} ORDER BY ${sortBy} ${sortOrder} LIMIT ? OFFSET ?`;
    const [rows] = await pool.query(dataSql, [...queryParams, limit, offset]);
    */

    // Simulated data output for demonstration
    const simulatedTotal = 25;
    const simulatedRows = Array.from({ length: limit }, (_, idx) => ({
      id: offset + idx + 1,
      name: `Student ${search ? search : ''} ${offset + idx + 1}`,
      email: `student${offset + idx + 1}@college.edu`,
      course: course || 'BCA',
      marks: 85
    })).filter(r => r.id <= simulatedTotal);

    return sendPaginated(
      res,
      simulatedRows,
      page,
      limit,
      simulatedTotal,
      'Combined query executed successfully'
    );
  } catch (err) {
    next(err);
  }
};

router.get('/students', validateQueryOptions, searchAndPaginateStudents);

export default router;
