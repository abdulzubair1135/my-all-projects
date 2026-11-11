import pool from '../config/db.js';

export const getCoursesWithDepartment = async () => {
  const query = `
    SELECT c.id, c.course_code, c.course_name, c.credits, 
           d.dept_name, d.dept_code
    FROM courses c
    INNER JOIN departments d ON c.department_id = d.id
    ORDER BY c.id DESC
  `;
  const [rows] = await pool.query(query);
  return rows;
};

export const getCourseById = async (id) => {
  const query = `
    SELECT c.id, c.course_code, c.course_name, c.credits, 
           d.dept_name, d.dept_code
    FROM courses c
    INNER JOIN departments d ON c.department_id = d.id
    WHERE c.id = ?
  `;
  const [rows] = await pool.query(query, [id]);
  return rows[0];
};

export const createCourse = async (data) => {
  const { course_code, course_name, credits, department_id } = data;
  const [result] = await pool.query(
    'INSERT INTO courses (course_code, course_name, credits, department_id) VALUES (?, ?, ?, ?)',
    [course_code, course_name, credits, department_id]
  );
  return result.insertId;
};

export const getAllDepartments = async () => {
  const [rows] = await pool.query('SELECT * FROM departments');
  return rows;
};
