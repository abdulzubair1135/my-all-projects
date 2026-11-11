import pool from '../config/db.js';

export const getAllStudents = async () => {
  const [rows] = await pool.query('SELECT * FROM students ORDER BY id DESC');
  return rows;
};

export const getStudentById = async (id) => {
  const [rows] = await pool.query('SELECT * FROM students WHERE id = ?', [id]);
  return rows[0];
};

export const createStudent = async (studentData) => {
  const { roll_no, name, email, department, gpa } = studentData;
  const [result] = await pool.query(
    'INSERT INTO students (roll_no, name, email, department, gpa) VALUES (?, ?, ?, ?, ?)',
    [roll_no, name, email, department, gpa]
  );
  return result.insertId;
};

export const updateStudent = async (id, studentData) => {
  const { roll_no, name, email, department, gpa } = studentData;
  const [result] = await pool.query(
    'UPDATE students SET roll_no = ?, name = ?, email = ?, department = ?, gpa = ? WHERE id = ?',
    [roll_no, name, email, department, gpa, id]
  );
  return result.affectedRows;
};

export const deleteStudent = async (id) => {
  const [result] = await pool.query('DELETE FROM students WHERE id = ?', [id]);
  return result.affectedRows;
};
