import pool from '../config/db.js';

export const getAll = async () => {
  const [rows] = await pool.query('SELECT * FROM employees ORDER BY id DESC');
  return rows;
};

export const getById = async (id) => {
  const [rows] = await pool.query('SELECT * FROM employees WHERE id = ?', [id]);
  return rows[0];
};

export const create = async (data) => {
  const { emp_code, name, email, designation, salary, department } = data;
  const [result] = await pool.query(
    'INSERT INTO employees (emp_code, name, email, designation, salary, department) VALUES (?, ?, ?, ?, ?, ?)',
    [emp_code, name, email, designation, salary, department]
  );
  return result.insertId;
};

export const update = async (id, data) => {
  const { emp_code, name, email, designation, salary, department } = data;
  const [result] = await pool.query(
    'UPDATE employees SET emp_code = ?, name = ?, email = ?, designation = ?, salary = ?, department = ? WHERE id = ?',
    [emp_code, name, email, designation, salary, department, id]
  );
  return result.affectedRows;
};

export const remove = async (id) => {
  const [result] = await pool.query('DELETE FROM employees WHERE id = ?', [id]);
  return result.affectedRows;
};
