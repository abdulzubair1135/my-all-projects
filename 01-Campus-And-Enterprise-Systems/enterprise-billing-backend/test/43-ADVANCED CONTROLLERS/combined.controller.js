/**
 * Master Combined Controller Module Exporting Full CRUD Suite
 * ES Module Format
 */

import { createStudent } from './create.controller.js';
import { getAllStudents, getStudentById } from './get.controller.js';
import { updateStudent } from './update.controller.js';
import { hardDeleteStudent, softDeleteStudent } from './delete.controller.js';
import { searchStudents } from './search.controller.js';
import { getPaginatedRecords } from './pagination.controller.js';

export const StudentController = {
  create: createStudent,
  getAll: getAllStudents,
  getById: getStudentById,
  update: updateStudent,
  hardDelete: hardDeleteStudent,
  softDelete: softDeleteStudent,
  search: searchStudents,
  getPaginated: getPaginatedRecords
};

export default StudentController;
