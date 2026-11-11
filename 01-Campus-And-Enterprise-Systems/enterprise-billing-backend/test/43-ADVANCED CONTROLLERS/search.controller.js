/**
 * Advanced Dedicated Search Controller Module
 * ES Module Format
 */

import { sendSuccess } from '../39-API RESPONSE PATTERNS/success-response.js';

/**
 * Executes keyword search queries over multiple database columns
 */
export const searchStudents = async (req, res, next) => {
  try {
    const { keyword = '', course = '' } = req.query;

    /* Database SQL Multi-Column Search:
    let sql = 'SELECT id, name, email, course, marks FROM students WHERE 1=1';
    const params = [];

    if (keyword) {
      sql += ' AND (name LIKE ? OR email LIKE ?)';
      params.push(`%${keyword}%`, `%${keyword}%`);
    }

    if (course) {
      sql += ' AND course = ?';
      params.push(course);
    }

    const [rows] = await pool.query(sql, params);
    return sendSuccess(res, rows, `Found ${rows.length} search results`);
    */

    const mockResults = [
      { id: 1, name: 'Rahul Sharma', email: 'rahul@example.com', course: course || 'BCA' }
    ];

    return sendSuccess(res, mockResults, `Search results for keyword "${keyword}"`);
  } catch (error) {
    next(error);
  }
};

export default searchStudents;
